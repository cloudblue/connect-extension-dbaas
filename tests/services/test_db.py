# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import re
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from connect.client import ClientError
from connect.eaas.core.inject.models import Context
from pymongo.errors import WriteError

from dbaas.constants import DBAction, DBStatus, DBWorkload
from dbaas.database import Collections
from dbaas.schemas import DatabaseInUpdate
from dbaas.services import DB

from tests.factories import CaseFactory, DBFactory, InstallationFactory, RegionFactory, UserFactory


@pytest.mark.asyncio
async def test_list_collection_is_empty(db, admin_context):
    results = await DB.list(db, Context(account_id='VA-123-456'))
    assert results == []

    results = await DB.list(db, admin_context)
    assert results == []


@pytest.mark.asyncio
async def test_list_no_account_dbs(db, admin_context):
    await db[Collections.DB].insert_many(DBFactory.create_batch(2))

    results = await DB.list(db, Context(account_id='PA-000-000'))
    assert results == []

    results = await DB.list(db, admin_context)
    assert len(results) == 2


@pytest.mark.parametrize('in_doc, out_doc', (
    ({}, {}),
    ({1: True, 'a': 'key'}, {1: True, 'a': 'key'}),
    (
        {'id': 'DB-1', 'cases': [], 'status': DBStatus.RECONFIGURING},
        {'id': 'DB-1', 'cases': [], 'status': DBStatus.RECONFIGURING},
    ),
    (
        {'cases': [1], 'status': DBStatus.REVIEWING},
        {'cases': [1], 'case': 1, 'status': DBStatus.REVIEWING},
    ),
    ({'cases': [1, 2]}, {'cases': [1, 2], 'case': 2}),
    ({'status': DBStatus.REVIEWING, 'credentials': 1}, {'status': DBStatus.REVIEWING}),
    ({'status': DBStatus.REVIEWING, 'x': 2}, {'status': DBStatus.REVIEWING, 'x': 2}),
    ({'status': DBStatus.ACTIVE, 'credentials': 2}, {'status': DBStatus.ACTIVE}),
    (
        {'status': DBStatus.RECONFIGURING, 'credentials': {1: True}},
        {'status': DBStatus.RECONFIGURING},
    ),
))
def test__db_document_repr(in_doc, out_doc):
    assert DB._db_document_repr(in_doc) == out_doc


@pytest.mark.parametrize('in_doc, out_doc', (
    ({}, {}),
    ({1: True, 'a': 'key'}, {1: True, 'a': 'key'}),
    (
        {
            'status': DBStatus.ACTIVE,
            'credentials': b'gAAAAABkEdPYFZffrdrEU5_jwzsBO-GstLDA2IYs8uAN7jGyQ4KRKw_'
                           b'CoxytmSLMdTi_NQ49Oe15RWgVtkbEFM2PAZ4wQI9sLQ==',
        },
        {'status': DBStatus.ACTIVE, 'credentials': {'1': 1}},
    ),
))
def test__db_document_repr_with_config(in_doc, out_doc, config):
    assert DB._db_document_repr(in_doc, config) == out_doc


@pytest.mark.asyncio
async def test_list_several_account_dbs(db, admin_context):
    account_id = 'PA-456'

    db1 = DBFactory(account_id=account_id, status=DBStatus.REVIEWING)
    deleted_db = DBFactory(account_id=account_id, status=DBStatus.DELETED)
    other_account_db = DBFactory(account_id='VA-700')
    db2 = DBFactory(account_id=account_id, status=DBStatus.ACTIVE)
    db3 = DBFactory(account_id=account_id, status=DBStatus.RECONFIGURING)
    await db[Collections.DB].insert_many([deleted_db, other_account_db, db2, db1, db3])

    results = await DB.list(db, Context(account_id=account_id))
    assert len(results) == 3
    assert [r['id'] for r in results] == [db['id'] for db in (db3, db2, db1)]

    results = await DB.list(db, admin_context)
    assert len(results) == 4
    assert [r['id'] for r in results] == [db['id'] for db in (db3, db2, other_account_db, db1)]


@pytest.mark.asyncio
async def test_retrieve_is_empty(db):
    result = await DB.retrieve('any', db, Context(account_id='VA-123-456'))

    assert result is None


@pytest.mark.asyncio
async def test_retrieve_is_from_other_account(db):
    db1 = DBFactory()
    await db[Collections.DB].insert_one(db1)

    result = await DB.retrieve(db1['id'], db, Context(account_id='PA-000-000'))
    assert result is None


@pytest.mark.asyncio
async def test_retrieve_is_deleted(db):
    db1 = DBFactory(status=DBStatus.DELETED)
    await db[Collections.DB].insert_one(db1)

    result = await DB.retrieve(db1['id'], db, Context(account_id=db1['account_id']))
    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize('status', (DBStatus.RECONFIGURING, DBStatus.ACTIVE, DBStatus.REVIEWING))
async def test_retrieve_is_found(db, status):
    db1 = DBFactory(status=status)
    await db[Collections.DB].insert_one(db1)

    result = await DB.retrieve(db1['id'], db, Context(account_id=db1['account_id']))
    assert result['id'] == db1['id']


@pytest.mark.asyncio
async def test__get_validated_region_document_valid_region(mocker):
    region = RegionFactory()
    p = mocker.patch('dbaas.services.Region.retrieve', return_value=region)

    result = await DB._get_validated_region_document({'region': {'id': region['id']}}, 'db')
    assert result == region

    p.assert_called_once_with(region['id'], 'db')


@pytest.mark.asyncio
async def test__get_validated_region_document_not_found(mocker):
    region = RegionFactory()
    p = mocker.patch('dbaas.services.Region.retrieve', return_value=None)

    with pytest.raises(ValueError) as e:
        await DB._get_validated_region_document({'region': {'id': region['id']}}, 'db')
    assert str(e.value) == 'Region does not exist.'

    p.assert_called_once_with(region['id'], 'db')


@pytest.mark.asyncio
async def test__get_validated_tech_contact_client_error(mocker):
    def raise_err(*a, **kw):
        raise ClientError(status_code=404)

    contact = UserFactory()
    p = mocker.patch('dbaas.services.ConnectAccountUser.retrieve', side_effect=raise_err)

    with pytest.raises(ClientError):
        await DB._get_validated_tech_contact(
            {'tech_contact': contact},
            Context(account_id='VA-123'),
            'client',
        )

    p.assert_called_once_with('VA-123', contact['id'], 'client')


@pytest.mark.asyncio
async def test__get_validated_tech_contact_is_inactive(mocker):
    contact = UserFactory(active=False)
    p = mocker.patch(
        'dbaas.services.ConnectAccountUser.retrieve',
        AsyncMock(return_value=contact),
    )

    with pytest.raises(ValueError) as e:
        await DB._get_validated_tech_contact(
            {'tech_contact': {'id': contact['id']}},
            Context(account_id='PA-123'),
            'client',
        )

    assert str(e.value) == 'Only active user can be a technical contact.'

    p.assert_called_once_with('PA-123', contact['id'], 'client')


@pytest.mark.asyncio
async def test__get_validated_tech_contact_valid_contact(async_client_mocker_factory, mocker):
    contact = UserFactory()
    p = mocker.patch(
        'dbaas.services.ConnectAccountUser.retrieve',
        AsyncMock(return_value=contact),
    )

    result = await DB._get_validated_tech_contact(
        {'tech_contact': {'id': contact['id']}},
        Context(account_id='VA-000-000'),
        'client',
    )

    assert result == contact

    p.assert_called_once_with('VA-000-000', contact['id'], 'client')


@pytest.mark.asyncio
async def test__get_actor_client_error(mocker):
    def raise_err(*a, **kw):
        raise ClientError(status_code=503)

    p = mocker.patch('dbaas.services.ConnectAccountUser.retrieve', side_effect=raise_err)

    with pytest.raises(ClientError):
        await DB._get_actor(
            Context(account_id='VA-123', user_id='UR-123'),
            'client',
        )

    p.assert_called_once_with('VA-123', 'UR-123', 'client')


@pytest.mark.asyncio
async def test__get_actor_ok(async_client_mocker_factory, mocker):
    user = UserFactory()
    p = mocker.patch('dbaas.services.ConnectAccountUser.retrieve', AsyncMock(return_value=user))

    result = await DB._get_actor(
        Context(account_id='PA-123', user_id=user['id']),
        'client',
    )

    assert result == user

    p.assert_called_once_with('PA-123', user['id'], 'client')


def test__prepare_db_document(mocker):
    data = {'name': 'DB-1'}
    context = Context(account_id='VA-123')
    region = RegionFactory(id='eu', name='Fr')
    tech_contact = UserFactory(id='X', name='Y', email='Z')
    actor = UserFactory(id='UR-1', name='abc')

    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    assert DB._prepare_db_document(data, context, region, tech_contact, actor) == {
        'name': 'DB-1',
        'account_id': 'VA-123',
        'status': 'reviewing',
        'events': {
            'created': {
                'at': 'DT',
                'by': {
                    'id': 'UR-1',
                    'name': 'abc',
                },
            },
        },
        'region': {
            'id': 'eu',
            'name': 'Fr',
        },
        'tech_contact': {
            'id': 'X',
            'name': 'Y',
            'email': 'Z',
        },
    }


@pytest.mark.asyncio
async def test__create_db_document_in_db_id_generated_immediately(db, mocker, config, logger):
    p = mocker.patch('dbaas.services.DB._generate_id', return_value='DB-1')
    data = {'x': True}

    async with await db.client.start_session() as db_session:
        result = await DB._create_db_document_in_db(data, db_session, config, logger)
    db_document = await db[Collections.DB].find_one({'id': 'DB-1'})

    assert result['id'] == 'DB-1'
    assert result['x'] is True and db_document['x'] is True

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1

    p.assert_called_once_with(config)
    logger.logger.warning.assert_not_called()
    logger.logger.exception.assert_not_called()


@pytest.mark.asyncio
async def test__create_db_document_in_db_id_generated_from_2_attempt(db, mocker, config, logger):
    await db[Collections.DB].insert_one({'id': 'DB-200'})
    p = mocker.patch('dbaas.services.DB._generate_id', side_effect=['DB-200', 'DB-100'])
    data = {'name': 'new Db'}

    async with await db.client.start_session() as db_session:
        result = await DB._create_db_document_in_db(data, db_session, config, logger)
    db_document = await db[Collections.DB].find_one({'id': 'DB-100'})

    assert result['id'] == 'DB-100'
    assert result['name'] == 'new Db' == db_document['name']

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 2

    p.assert_has_calls([mocker.call(config), mocker.call(config)])
    logger.logger.warning.assert_called_once_with('ID regeneration attempt %d...', 1)
    logger.logger.exception.assert_not_called()


@pytest.mark.asyncio
async def test__create_db_document_in_db_id_generation_error(db, mocker, config, logger):
    await db[Collections.DB].insert_one({'id': 'DB-300'})
    p = mocker.patch('dbaas.services.DB._generate_id', return_value='DB-300')

    with pytest.raises(ValueError) as e:
        async with await db.client.start_session() as db_session:
            await DB._create_db_document_in_db({}, db_session, config, logger)

    assert str(e.value) == 'ID generation error.'

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1

    p.assert_has_calls([mocker.call(config), mocker.call(config), mocker.call(config)])
    logger.logger.warning.assert_has_calls([
        mocker.call('ID regeneration attempt %d...', 1),
        mocker.call('ID regeneration attempt %d...', 2),
    ])
    logger.logger.exception.assert_not_called()


@pytest.mark.asyncio
async def test__create_db_document_in_db_id_operation_error(db, mocker, config, logger):
    def raise_err(*a):
        raise WriteError('err')

    p = mocker.patch('dbaas.services.DB._generate_id', side_effect=raise_err)
    with pytest.raises(ClientError) as e:
        async with await db.client.start_session() as db_session:
            await DB._create_db_document_in_db({}, db_session, config, logger)

    assert e.value.status_code == 503

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 0

    p.assert_called_once_with(config)
    logger.logger.warning.assert_not_called()
    logger.logger.exception.called_once_with('DB writing error.')


@pytest.mark.parametrize('execution_number', range(5))
def test__generate_id_default(config, execution_number):
    assert re.fullmatch(r'DBPG\-\d{5}', DB._generate_id(config))


def test__generate_id_with_changed_config():
    config = {
        'DB_ID_RANDOM_LENGTH': 3,
        'DB_ID_PREFIX': 'DBM',
    }

    assert re.fullmatch(r'DBM\-\d{3}', DB._generate_id(config))


@pytest.mark.asyncio
async def test__create_db_document_admin_document_created(db, admin_context, config, mocker):
    context = admin_context
    context.installation_id = 'EIN-123'
    data = {'name': 'test'}
    installation_p = mocker.patch('dbaas.services.ConnectInstallation.retrieve')
    case_p = mocker.patch('dbaas.services.ConnectHelpdeskCase.create_from_db_document')
    db_p = mocker.patch('dbaas.services.DB._create_db_document_in_db', return_value={'id': 'DB'})
    client = mocker.MagicMock()

    result = await DB._create_db_document(
        data,
        db,
        context,
        client=client,
        config=config,
    )

    assert result == {'id': 'DB'}

    installation_p.assert_not_called()
    case_p.assert_not_called()

    db_p_call = db_p.call_args[0]
    assert db_p_call[0] == data
    assert db_p_call[2] == config
    assert db_p_call[3] == client.logger


@pytest.mark.asyncio
async def test__create_db_document_common_document_created(db, config, mocker):
    installation = InstallationFactory()
    context = Context(installation_id=installation['id'])
    helpdesk_case = CaseFactory()

    data = {'description': 'desc'}
    installation_p = mocker.patch(
        'dbaas.services.ConnectInstallation.retrieve',
        AsyncMock(return_value=installation),
    )
    case_p = mocker.patch(
        'dbaas.services.ConnectHelpdeskCase.create_from_db_document',
        AsyncMock(return_value=helpdesk_case),
    )
    db_p = mocker.patch('dbaas.services.DB._create_db_document_in_db', return_value={
        'id': 'DB1',
        'description': 'desc',
    })

    db_s_p = AsyncMock()
    mocker.patch(
        'dbaas.services.DB._db_collection_from_db_session',
        return_value=mocker.MagicMock(update_one=db_s_p),
    )
    client = mocker.MagicMock()

    result = await DB._create_db_document(
        data,
        db,
        context,
        client=client,
        config=config,
    )

    assert result == {
        'id': 'DB1',
        'description': 'desc',
        'cases': [{'id': helpdesk_case['id']}],
    }

    installation_p.assert_called_once_with(installation['id'], client)

    case_p.assert_called_once_with(
        result,
        action=DBAction.CREATE,
        description='desc',
        installation=installation,
        client=client,
    )

    db_p_call = db_p.call_args[0]
    assert db_p_call[0] == data
    assert db_p_call[2] == config
    assert db_p_call[3] == client.logger

    db_s_p_call = db_s_p.call_args[0]
    assert db_s_p_call[0] == {'id': 'DB1'}
    assert db_s_p_call[1] == {'$set': {'cases': [{'id': helpdesk_case['id']}]}}


@pytest.mark.asyncio
@pytest.mark.parametrize('error_cls', (ValueError, ClientError))
async def test__create_db_document_error(db, error_cls, admin_context, mocker, config):
    def raise_err(*a):
        raise error_cls('err')

    mocker.patch('dbaas.services.DB._create_db_document_in_db', side_effect=raise_err)

    with pytest.raises(error_cls):
        await DB._create_db_document(
            {},
            db,
            admin_context,
            client=mocker.MagicMock(),
            config='config',
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('context_uid, actor, am_call_count', (
    ('UR-123-456', {'id': 'UR-123-456'}, 0),
    ('UR-000-000', {'id': 'UR-000-000'}, 1),
))
async def test_create_ok(mocker, context_uid, am_call_count, actor):
    data = {'name': 'patch'}
    context = Context(user_id=context_uid)

    gvrd_p = mocker.patch(
        'dbaas.services.DB._get_validated_region_document',
        AsyncMock(return_value='region_doc'),
    )
    gvtc_p = mocker.patch(
        'dbaas.services.DB._get_validated_tech_contact',
        AsyncMock(return_value={'id': 'UR-123-456'}),
    )
    ga_p = mocker.patch(
        'dbaas.services.DB._get_actor',
        AsyncMock(return_value=actor),
    )
    pdd_p = mocker.patch('dbaas.services.DB._prepare_db_document', return_value='prepared_db_doc')
    cdd_p = mocker.patch(
        'dbaas.services.DB._create_db_document',
        AsyncMock(return_value='inserted_db_doc'),
    )
    ddr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='result')

    result = await DB.create(
        data,
        'db',
        context,
        'client',
        'config',
    )

    assert result == 'result'

    gvrd_p.assert_called_once_with(data, 'db')
    gvtc_p.assert_called_once_with(data, context, 'client')
    assert ga_p.call_count == am_call_count
    pdd_p.assert_called_once_with(
        data, context, 'region_doc', {'id': 'UR-123-456'}, actor,
    )
    cdd_p.assert_called_once_with('prepared_db_doc', 'db', context, 'client', 'config')
    ddr_p.assert_called_once_with('inserted_db_doc')


@pytest.mark.asyncio
@pytest.mark.parametrize('error_cls', (ValueError, ClientError))
async def test_create_error(error_cls, mocker):
    def raise_err(*a):
        raise error_cls('err')

    mocker.patch('dbaas.services.DB._get_validated_region_document', side_effect=raise_err)

    with pytest.raises(error_cls):
        await DB.create(
            {},
            'db',
            'context',
            'client',
            'config',
        )


@pytest.mark.asyncio
@pytest.mark.parametrize('data', ({}, {'name': None, 'description': None, 'tech_contact': None}))
async def test_update_empty_data(data, mocker):
    db_document = DBFactory()

    contact_p = mocker.patch('dbaas.services.DB._get_validated_tech_contact')
    actor_p = mocker.patch('dbaas.services.DB._get_actor')
    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='result')

    result = await DB.update(db_document, data, 'db', 'context', 'client')

    assert result == 'result'

    contact_p.assert_not_called()
    actor_p.assert_not_called()
    repr_p.assert_called_once_with(db_document)


@pytest.mark.asyncio
async def test_update_no_changes(mocker, db):
    db_document = DBFactory()
    data = DatabaseInUpdate(**db_document).dict()
    await db[Collections.DB].insert_one(db_document)

    contact_p = mocker.patch('dbaas.services.DB._get_validated_tech_contact')
    actor_p = mocker.patch('dbaas.services.DB._get_actor')
    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='result')

    result = await DB.update(db_document, data, 'db', 'context', 'client')
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'result'
    assert 'updated' not in db_document_from_db['events']

    contact_p.assert_not_called()
    actor_p.assert_not_called()
    repr_p.assert_called_once_with(db_document)


@pytest.mark.asyncio
async def test_update_partial_update_ok(mocker, db):
    db_document = DBFactory(name='old', description='old')
    actor = UserFactory(id='UR-123', name='123')
    data = {'name': 'new', 'tech_contact': None}
    updated_event = {
        'at': 'DT',
        'by': {
            'id': 'UR-123',
            'name': '123',
        },
    }
    await db[Collections.DB].insert_one(db_document)

    contact_p = mocker.patch('dbaas.services.DB._get_validated_tech_contact')
    actor_p = mocker.patch('dbaas.services.DB._get_actor', AsyncMock(return_value=actor))
    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='partial')
    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    result = await DB.update(db_document, data, db, 'context', 'client')
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'partial'

    contact_p.assert_not_called()
    actor_p.assert_called_once_with('context', 'client')

    db_document['name'] = 'new'
    db_document['events'].update(updated_event)
    repr_p.assert_called_once_with(db_document)
    assert db_document_from_db['name'] == 'new'
    assert db_document_from_db['events']['created']
    assert db_document_from_db['events']['updated'] == updated_event
    assert db_document_from_db['description'] == 'old'
    assert db_document_from_db['tech_contact'] == db_document['tech_contact']

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
async def test_update_full_update_ok(mocker, db):
    db_document = DBFactory(name='old', description='old', tech_contact__id='UR-000')
    actor = UserFactory(id='UR-456', name='456')
    tech_contact = UserFactory(id='UR-789', name='789', email='x@y.test')

    data = {'name': 'new', 'description': 'new', 'tech_contact': tech_contact}
    updated_event = {
        'at': 'DT',
        'by': {
            'id': 'UR-456',
            'name': '456',
        },
    }
    await db[Collections.DB].insert_one(db_document)

    contact_p = mocker.patch(
        'dbaas.services.DB._get_validated_tech_contact',
        AsyncMock(return_value=tech_contact),
    )
    actor_p = mocker.patch('dbaas.services.DB._get_actor', AsyncMock(return_value=actor))
    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='full')
    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    result = await DB.update(db_document, data, db, 'context', 'client', config='config')
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'full'

    contact_p.assert_called_once_with(data, 'context', 'client')
    actor_p.assert_called_once_with('context', 'client')

    db_document['name'] = 'new'
    db_document['description'] = 'new'
    db_document['tech_contact'] = {
        'id': 'UR-789',
        'name': '789',
        'email': 'x@y.test',
    }
    db_document['events'].update(updated_event)
    repr_p.assert_called_once_with(db_document)
    assert db_document_from_db['name'] == 'new'
    assert db_document_from_db['events']['created']
    assert db_document_from_db['events']['updated'] == updated_event
    assert db_document_from_db['description'] == 'new'
    assert db_document_from_db['tech_contact'] == db_document['tech_contact']

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('error_cls', (ValueError, ClientError))
async def test_update_error(error_cls, mocker):
    def raise_err(*a):
        raise error_cls('err')

    mocker.patch('dbaas.services.DB._get_actor', side_effect=raise_err)

    with pytest.raises(error_cls):
        await DB.update({}, {'name': True}, 'db', 'context', 'client')


@pytest.mark.asyncio
@pytest.mark.parametrize('status', (DBStatus.REVIEWING, DBStatus.RECONFIGURING))
async def test_reconfigure_wrong_db_status(status, mocker):
    db_document = DBFactory(status=status)
    actor_p = mocker.patch('dbaas.services.DB._get_actor')

    with pytest.raises(ValueError) as e:
        await DB.reconfigure(db_document, {}, 'db', 'context', 'client')

    assert str(e.value) == 'Only active DB can be reconfigured.'

    actor_p.assert_not_called()


@pytest.mark.asyncio
async def test_reconfigure_by_admin(mocker, admin_context, db):
    db_document = DBFactory(status=DBStatus.ACTIVE)
    actor = UserFactory(id='UR-456', name='456')
    data = {'action': DBAction.UPDATE}
    reconfigured_event = {
        'at': 'DT',
        'by': {
            'id': 'UR-456',
            'name': '456',
        },
    }
    await db[Collections.DB].insert_one(db_document)

    actor_p = mocker.patch('dbaas.services.DB._get_actor', AsyncMock(return_value=actor))
    installation_p = mocker.patch('dbaas.services.ConnectInstallation.retrieve')
    case_p = mocker.patch('dbaas.services.ConnectHelpdeskCase.create_from_db_document')
    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='admin')
    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    result = await DB.reconfigure(db_document, data, db, admin_context, 'client')
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'admin'

    actor_p.assert_called_once_with(admin_context, 'client')
    installation_p.assert_not_called()
    case_p.assert_not_called()

    db_document['status'] = DBStatus.RECONFIGURING
    db_document['events'].update(reconfigured_event)
    repr_p.assert_called_once_with(db_document)
    assert db_document_from_db['status'] == DBStatus.RECONFIGURING
    assert db_document_from_db['cases'] == []
    assert db_document_from_db['events']['created']
    assert db_document_from_db['events']['reconfigured'] == reconfigured_event

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('action', (DBAction.DELETE, DBAction.UPDATE))
@pytest.mark.parametrize('details, case_desc', ((None, '-'), ('des crip', 'des crip')))
async def test_reconfigure_by_common_installation(mocker, db, action, details, case_desc):
    existing_helpdesk_case = CaseFactory()
    db_document = DBFactory(status=DBStatus.ACTIVE, cases=[existing_helpdesk_case])

    actor = UserFactory(id='UR-000', name='user')
    installation = InstallationFactory()
    context = Context(user_id=actor['id'], installation_id=installation['id'])
    helpdesk_case = CaseFactory()
    data = {'action': action, 'details': details}
    reconfigured_event = {
        'at': 'DT',
        'by': {
            'id': 'UR-000',
            'name': 'user',
        },
    }
    await db[Collections.DB].insert_one(db_document)

    actor_p = mocker.patch('dbaas.services.DB._get_actor', AsyncMock(return_value=actor))
    installation_p = mocker.patch(
        'dbaas.services.ConnectInstallation.retrieve',
        AsyncMock(return_value=installation),
    )
    case_p = mocker.patch(
        'dbaas.services.ConnectHelpdeskCase.create_from_db_document',
        AsyncMock(return_value=helpdesk_case),
    )
    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='common')
    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    result = await DB.reconfigure(db_document, data, db, context, 'client', config='config')
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'common'

    actor_p.assert_called_once_with(context, 'client')
    installation_p.assert_called_once_with(installation['id'], 'client')
    case_p.assert_called_once_with(
        db_document,
        action=action,
        description=case_desc,
        installation=installation,
        client='client',
    )

    db_document['status'] = DBStatus.RECONFIGURING
    db_document['events'].update(reconfigured_event)
    repr_p.assert_called_once_with(db_document)
    assert db_document_from_db['status'] == DBStatus.RECONFIGURING
    assert db_document_from_db['cases'] == [existing_helpdesk_case, {'id': helpdesk_case['id']}]
    assert db_document_from_db['events']['created']
    assert db_document_from_db['events']['reconfigured'] == reconfigured_event

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('error_cls', (ValueError, ClientError))
async def test_reconfigure_error(error_cls, mocker):
    def raise_err(*a):
        raise error_cls('err')

    db_document = DBFactory(status=DBStatus.ACTIVE)
    mocker.patch('dbaas.services.DB._get_actor', side_effect=raise_err)

    with pytest.raises(error_cls):
        await DB.reconfigure(db_document, {}, 'db', 'context', 'client')


@pytest.mark.asyncio
@pytest.mark.parametrize('status', (DBStatus.REVIEWING, DBStatus.RECONFIGURING))
async def test_delete(mocker, db, status):
    db_document = DBFactory(status=status)

    deleted_event = {'at': 'DT'}
    await db[Collections.DB].insert_one(db_document)

    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='delete')
    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    result = await DB.delete(db_document, db, config='config')
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'delete'

    db_document['status'] = DBStatus.DELETED
    db_document['events'].update(deleted_event)
    repr_p.assert_called_once_with(db_document)
    assert db_document_from_db['status'] == DBStatus.DELETED
    assert db_document_from_db['events']['created']
    assert db_document_from_db['events']['deleted'] == deleted_event

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
async def test_activate_active_without_credentials(mocker, db, config):
    db_document = DBFactory(status=DBStatus.ACTIVE)
    del db_document['credentials']

    await db[Collections.DB].insert_one(db_document)

    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='aa')

    result = await DB.activate(db_document, db=db, data={}, config=config, client='client')
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'aa'

    db_document['status'] = DBStatus.ACTIVE
    repr_p.assert_called_once_with(db_document, config=config)
    assert db_document_from_db['status'] == DBStatus.ACTIVE
    assert db_document_from_db['events']['created']
    assert 'activated' not in db_document_from_db['events']
    assert 'credentials' not in db_document_from_db['events']

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
async def test_activate_reviewing_without_credentials(config):
    db_document = DBFactory(status=DBStatus.REVIEWING)

    with pytest.raises(ValueError) as e:
        await DB.activate(db_document, db='db', data={}, config=config)

    assert str(e.value) == 'Credentials are required for DB activation.'


@pytest.mark.asyncio
async def test_activate_reconfiguring_without_credentials(mocker, db, config):
    db_document = DBFactory(status=DBStatus.RECONFIGURING, workload=DBWorkload.MEDIUM)
    activated_event = {'at': 'DT'}
    data = {'workload': DBWorkload.LARGE}

    await db[Collections.DB].insert_one(db_document)

    repr_p = mocker.patch('dbaas.services.DB._db_document_repr', return_value='ra')
    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    result = await DB.activate(db_document, db=db, data=data, config=config)
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'ra'

    db_document['status'] = DBStatus.ACTIVE
    db_document['workload'] = DBWorkload.LARGE
    db_document['events'].update(activated_event)
    repr_p.assert_called_once_with(db_document, config=config)
    assert db_document_from_db['status'] == DBStatus.ACTIVE
    assert db_document_from_db['events']['created']
    assert db_document_from_db['events']['activated'] == activated_event
    assert db_document_from_db['credentials'] == db_document['credentials']
    assert db_document_from_db['workload'] == DBWorkload.LARGE

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('status', (DBStatus.REVIEWING, DBStatus.RECONFIGURING))
async def test_activate_with_credentials(mocker, db, status, config):
    db_document = DBFactory(status=status)
    activated_event = {'at': 'DT'}
    credentials = {'a': 1, 'username': 'user', 'b': True}

    await db[Collections.DB].insert_one(db_document)

    mocker.patch('dbaas.services.DB._db_document_repr', return_value='rc')
    dt = mocker.patch('dbaas.services.datetime', wraps=datetime)
    dt.now.return_value = 'DT'

    result = await DB.activate(db_document, db=db, data={'credentials': credentials}, config=config)
    db_document_from_db = await db[Collections.DB].find_one({'id': db_document['id']})

    assert result == 'rc'

    assert db_document_from_db['status'] == DBStatus.ACTIVE
    assert db_document_from_db['events']['created']
    assert db_document_from_db['events']['activated'] == activated_event
    assert db_document_from_db['workload'] == db_document['workload']
    assert DB._decrypt_dict(db_document_from_db['credentials'], config) == credentials

    count_docs = await db[Collections.DB].count_documents({})
    assert count_docs == 1
