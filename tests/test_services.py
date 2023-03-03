# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from connect.eaas.core.inject.models import Context

from dbaas.constants import DBStatus
from dbaas.database import Collections
from dbaas.services import DB, Region

from tests.factories import CaseFactory, DBFactory, RegionFactory


@pytest.mark.asyncio
async def test_db_list_collection_is_empty(db):
    results = await DB.list(db, Context(account_id='VA-123-456'))

    assert results == []


@pytest.mark.asyncio
async def test_db_list_no_account_dbs(db):
    db[Collections.DB].insert_many(DBFactory.create_batch(2))

    results = await DB.list(db, Context(account_id='PA-000-000'))
    assert results == []


@pytest.mark.asyncio
async def test_db_list_several_account_dbs(db):
    account_id = 'PA-456'

    db1 = DBFactory(account_id=account_id, status=DBStatus.REVIEWING)
    deleted_db = DBFactory(account_id=account_id, status=DBStatus.DELETED)
    other_account_db = DBFactory(account_id='VA-700')
    db2 = DBFactory(account_id=account_id, status=DBStatus.ACTIVE, cases=[CaseFactory(id='CS-1')])
    del db2['credentials']
    db3 = DBFactory(
        account_id=account_id,
        status=DBStatus.RECONFIGURING,
        cases=[CaseFactory(id='CS-3'), CaseFactory(id='CS-2')],
    )
    db[Collections.DB].insert_many([deleted_db, other_account_db, db2, db1, db3])

    results = await DB.list(db, Context(account_id=account_id))

    assert len(results) == 3
    assert [r['id'] for r in results] == [db['id'] for db in (db1, db2, db3)]

    assert db1['credentials'] and ('credentials' not in results[0])
    assert 'credentials' not in results[1]
    assert db3['credentials'] and results[2]['credentials'] == db3['credentials']

    assert 'case' not in results[0]
    assert results[1]['case'] == {'id': 'CS-1'}
    assert results[2]['case'] == {'id': 'CS-2'}


@pytest.mark.asyncio
async def test_db_retrieve_is_empty(db):
    result = await DB.retrieve('any', db, Context(account_id='VA-123-456'))

    assert result is None


@pytest.mark.asyncio
async def test_db_retrieve_is_from_other_account(db):
    db1 = DBFactory()
    db[Collections.DB].insert_one(db1)

    result = await DB.retrieve(db1['id'], db, Context(account_id='PA-000-000'))
    assert result is None


@pytest.mark.asyncio
async def test_db_retrieve_is_deleted(db):
    db1 = DBFactory(status=DBStatus.DELETED)
    db[Collections.DB].insert_one(db1)

    result = await DB.retrieve(db1['id'], db, Context(account_id=db1['account_id']))
    assert result is None


@pytest.mark.asyncio
@pytest.mark.parametrize('status', (DBStatus.RECONFIGURING, DBStatus.ACTIVE, DBStatus.REVIEWING))
async def test_db_retrieve_is_found(db, mocker, status):
    p = mocker.patch('dbaas.services.DB._modify_db_document', side_effect=lambda i: i)

    db1 = DBFactory(status=status)
    db[Collections.DB].insert_one(db1)

    result = await DB.retrieve(db1['id'], db, Context(account_id=db1['account_id']))
    assert result['id'] == db1['id']

    p.assert_called_once()


@pytest.mark.asyncio
async def test_region_list_is_empty(db):
    results = await Region.list(db)

    assert results == []


@pytest.mark.asyncio
async def test_region_list_several_regions(db):
    r1 = RegionFactory(name='Europe')
    r2 = RegionFactory(name='Asia')
    db[Collections.REGION].insert_many([r1, r2])

    results = await Region.list(db)

    assert len(results) == 2
    assert [r['id'] for r in results] == [r['id'] for r in (r2, r1)]
