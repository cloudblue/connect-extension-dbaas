# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, CloudBlue
# All rights reserved.
#

import pytest
from connect.client import ClientError
from fastapi.encoders import jsonable_encoder
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from dbaas.constants import DBAction
from dbaas.schemas import (
    DatabaseInCreate,
    DatabaseInUpdate,
    DatabaseOutDetail,
    DatabaseOutList,
    RegionOut,
)
from dbaas.webapp import client_error_handler, DBaaSWebApplication, na_exception_handler

from tests.constants import DB_DEP_MOCK, INSTALLATION_CLIENT_DEP_MOCK
from tests.factories import DBFactory, RegionFactory


DB_API = '/api/v1/databases'
REGION_API = '/api/v1/regions'


@pytest.mark.asyncio
@pytest.mark.parametrize('error, body, code', (
    (ClientError(message='abc', status_code=400), b'{"message":"abc"}', 400),
    (ClientError(message='abc', status_code=404), b'{"message":"abc"}', 400),
    (ClientError(message='abc'), b'{"message":"Service Unavailable."}', 503),
    (ClientError(message='abc', status_code=500), b'{"message":"Service Unavailable."}', 503),
    (ClientError(errors=['cbd'], status_code=503), b'{"message":"Service Unavailable."}', 503),
    (ClientError(errors=['cbd', 'abc'], message="x", status_code=404), b'{"message":"cbd"}', 400),
))
async def test_client_error_handler(error, body, code):
    result = await client_error_handler(None, error)

    assert result.status_code == code
    assert result.body == body


@pytest.mark.asyncio
@pytest.mark.parametrize('error_cls', (PyMongoError, ServerSelectionTimeoutError))
async def test_na_exception_handler(error_cls):
    result = await na_exception_handler(None, error_cls)

    assert result.status_code == 503
    assert result.body == b'{"message":"Service Unavailable."}'


def test_get_exception_handlers():
    handlers = DBaaSWebApplication.get_exception_handlers({RuntimeError: None})

    assert handlers == {
        ClientError: client_error_handler,
        PyMongoError: na_exception_handler,
    }


@pytest.mark.asyncio
async def test_on_start(mocker):
    p = mocker.patch('dbaas.webapp.prepare_db')

    await DBaaSWebApplication().on_startup(1, 2)

    p.assert_called_once_with(1, 2)


def test_list_databases_is_empty(api_client, mocker, common_context):
    p = mocker.patch('dbaas.webapp.DB.list', return_value=[])

    response = api_client.get(DB_API)
    assert response.status_code == 200
    assert response.json() == []

    p.assert_called_once_with(DB_DEP_MOCK, common_context)


def test_list_databases_several_dbs(api_client, mocker, common_context):
    db_documents = DBFactory.create_batch(2, account_id='VA-123')
    p = mocker.patch('dbaas.webapp.DB.list', return_value=db_documents)

    response = api_client.get(DB_API)
    assert response.status_code == 200
    assert response.json() == jsonable_encoder([
        DatabaseOutList(**db_documents[0]),
        DatabaseOutList(**db_documents[1]),
    ])

    p.assert_called_once_with(DB_DEP_MOCK, common_context)


def test_retrieve_database_200(api_client, mocker, common_context, config):
    db_document = DBFactory()
    p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=db_document)

    response = api_client.get(f'{DB_API}/DB-456-789')
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    p.assert_called_once_with('DB-456-789', DB_DEP_MOCK, common_context, config=config)


def test_retrieve_database_404(api_client, mocker, common_context, config):
    p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)

    response = api_client.get(f'{DB_API}/DB-123')
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    p.assert_called_once_with('DB-123', DB_DEP_MOCK, common_context, config=config)


def test_create_database_201(api_client, mocker, config, common_context):
    db_document = DBFactory()
    p = mocker.patch('dbaas.webapp.DB.create', return_value=db_document)
    data = DatabaseInCreate(**db_document).dict()

    response = api_client.post(DB_API, json=data)
    assert response.status_code == 201
    assert response.json() == jsonable_encoder(DatabaseOutList(**db_document))

    p.assert_called_once_with(
        data,
        db=DB_DEP_MOCK,
        context=common_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=config,
    )


def test_create_database_400(api_client, mocker, config, common_context):
    def raise_ve(*a, **kw):
        raise ValueError('test')

    p = mocker.patch('dbaas.webapp.DB.create', side_effect=raise_ve)
    data = DBFactory(events=None)

    response = api_client.post(DB_API, json=data)
    assert response.status_code == 400
    assert response.json() == {'message': 'test'}

    p.assert_called_once_with(
        DatabaseInCreate(**data).dict(),
        db=DB_DEP_MOCK,
        context=common_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=config,
    )


def test_create_database_422(api_client, mocker):
    p = mocker.patch('dbaas.webapp.DB.create')
    data = {'invalid': 'data'}

    response = api_client.post(DB_API, json=data)
    assert response.status_code == 422
    assert response.json()

    p.assert_not_called()


def test_update_database_200(api_client, mocker, config, common_context):
    db_document = DBFactory()
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'a': True})
    update_p = mocker.patch('dbaas.webapp.DB.update', return_value=db_document)
    data = DatabaseInUpdate(**db_document).dict()

    response = api_client.put(f'{DB_API}/{db_document_id}', json=data)
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, common_context)
    update_p.assert_called_once_with(
        {'a': True},
        data=data,
        db=DB_DEP_MOCK,
        context=common_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=None,
    )


def test_update_database_400(api_client, mocker, config, common_context):
    def raise_ve(*a, **kw):
        raise ValueError('test1')

    db_document = DBFactory(events=None)
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'some': 'mock'})
    update_p = mocker.patch('dbaas.webapp.DB.update', side_effect=raise_ve)
    data = DatabaseInUpdate(**db_document).dict()

    response = api_client.put(f'{DB_API}/{db_document_id}', json=data)
    assert response.status_code == 400
    assert response.json() == {'message': 'test1'}

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, common_context)
    update_p.assert_called_once_with(
        {'some': 'mock'},
        data=data,
        db=DB_DEP_MOCK,
        context=common_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=None,
    )


def test_update_database_404(api_client, mocker, config, common_context):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)
    update_p = mocker.patch('dbaas.webapp.DB.update')

    response = api_client.put(f'{DB_API}/DB-123', json={})
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    retrieve_p.assert_called_once_with('DB-123', DB_DEP_MOCK, common_context)
    update_p.assert_not_called()


def test_update_database_422(api_client, mocker, config):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve')
    update_p = mocker.patch('dbaas.webapp.DB.update')

    response = api_client.put(f'{DB_API}/DB-456', json={'name': {}})
    assert response.status_code == 422
    assert response.json()

    retrieve_p.assert_not_called()
    update_p.assert_not_called()


@pytest.mark.parametrize('action', (DBAction.DELETE, DBAction.UPDATE))
def test_reconfigure_database_200(api_client, mocker, config, common_context, action):
    db_document = DBFactory()
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'b': True})
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure', return_value=db_document)
    data = {'action': action}

    response = api_client.post(f'{DB_API}/{db_document_id}/reconfigure', json=data)
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, common_context)
    reconfigure_p.assert_called_once_with(
        {'b': True},
        data={'action': action, 'details': None},
        db=DB_DEP_MOCK,
        context=common_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=None,
    )


def test_reconfigure_database_400(api_client, mocker, config, common_context):
    def raise_ve(*a, **kw):
        raise ValueError('test2')

    db_document = DBFactory(events=None)
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'some': 'mock'})
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure', side_effect=raise_ve)
    data = {'action': DBAction.UPDATE, 'details': 'x'}

    response = api_client.post(f'{DB_API}/{db_document_id}/reconfigure', json=data)
    assert response.status_code == 400
    assert response.json() == {'message': 'test2'}

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, common_context)
    reconfigure_p.assert_called_once_with(
        {'some': 'mock'},
        data=data,
        db=DB_DEP_MOCK,
        context=common_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=None,
    )


def test_reconfigure_database_404(api_client, mocker, config, common_context):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure')
    data = {'action': DBAction.DELETE}

    response = api_client.post(f'{DB_API}/DB-789/reconfigure', json=data)
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    retrieve_p.assert_called_once_with('DB-789', DB_DEP_MOCK, common_context)
    reconfigure_p.assert_not_called()


def test_reconfigure_database_422(api_client, mocker, config):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve')
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure')

    response = api_client.post(f'{DB_API}/DB-456/reconfigure', json={'case': None})
    assert response.status_code == 422
    assert response.json()

    retrieve_p.assert_not_called()
    reconfigure_p.assert_not_called()


def test_activate_database_200(admin_api_client, mocker, config, admin_context):
    db_document = DBFactory()
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'c': True})
    activate_p = mocker.patch('dbaas.webapp.DB.activate', return_value=db_document)
    data = {}

    response = admin_api_client.post(f'{DB_API}/{db_document_id}/activate', json=data)
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, admin_context)
    activate_p.assert_called_once_with(
        {'c': True},
        data={'credentials': None, 'workload': None},
        db=DB_DEP_MOCK,
        context=admin_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=config,
    )


def test_activate_database_400(admin_api_client, mocker, config, admin_context):
    def raise_ve(*a, **kw):
        raise ValueError('activate')

    db_document = DBFactory()
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'abc': 'x'})
    activate_p = mocker.patch('dbaas.webapp.DB.activate', side_effect=raise_ve)
    data = {
        'credentials': {
            'username': 'user',
            'password': '!',
            'host': 'example.com',
            'name': None,
        },
        'workload': None,
    }

    response = admin_api_client.post(f'{DB_API}/{db_document_id}/activate', json=data)
    assert response.status_code == 400
    assert response.json() == {'message': 'activate'}

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, admin_context)
    activate_p.assert_called_once_with(
        {'abc': 'x'},
        data=data,
        db=DB_DEP_MOCK,
        context=admin_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=config,
    )


def test_activate_database_403(api_client, mocker):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve')
    activate_p = mocker.patch('dbaas.webapp.DB.activate')

    response = api_client.post(f'{DB_API}/DB-456/activate', json={})
    assert response.status_code == 403
    assert response.json() == {'message': 'Permission denied.'}

    retrieve_p.assert_not_called()
    activate_p.assert_not_called()


def test_activate_database_404(admin_api_client, mocker, config, admin_context):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)
    activate_p = mocker.patch('dbaas.webapp.DB.activate')

    response = admin_api_client.post(f'{DB_API}/DB-789/activate', json={})
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    retrieve_p.assert_called_once_with('DB-789', DB_DEP_MOCK, admin_context)
    activate_p.assert_not_called()


def test_activate_database_422(admin_api_client, mocker, config, admin_context):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve')
    activate_p = mocker.patch('dbaas.webapp.DB.activate')
    data = {'credentials': 5}

    response = admin_api_client.post(f'{DB_API}/DB-223/activate', json=data)
    assert response.status_code == 422
    assert response.json()

    retrieve_p.assert_not_called()
    activate_p.assert_not_called()


def test_delete_database_204(admin_api_client, mocker, config, admin_context):
    db_document = DBFactory()
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'doc': 'tor'})
    delete_p = mocker.patch('dbaas.webapp.DB.delete', return_value=db_document)

    response = admin_api_client.delete(f'{DB_API}/{db_document_id}')
    assert response.status_code == 204
    assert not response.text

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, admin_context)
    delete_p.assert_called_once_with(
        {'doc': 'tor'},
        data=None,
        db=DB_DEP_MOCK,
        context=admin_context,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=None,
    )


def test_delete_database_403(api_client, mocker):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve')
    delete_p = mocker.patch('dbaas.webapp.DB.delete')

    response = api_client.delete(f'{DB_API}/DB-456')
    assert response.status_code == 403
    assert response.json() == {'message': 'Permission denied.'}

    retrieve_p.assert_not_called()
    delete_p.assert_not_called()


def test_delete_database_404(admin_api_client, mocker, config, admin_context):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)
    delete_p = mocker.patch('dbaas.webapp.DB.delete')

    response = admin_api_client.delete(f'{DB_API}/DB-789')
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    retrieve_p.assert_called_once_with('DB-789', DB_DEP_MOCK, admin_context)
    delete_p.assert_not_called()


def test_list_regions(api_client, mocker):
    region_documents = RegionFactory.create_batch(2)
    p = mocker.patch('dbaas.webapp.Region.list', return_value=region_documents)

    response = api_client.get(REGION_API)
    assert response.status_code == 200
    assert response.json() == jsonable_encoder([
        RegionOut(**region_documents[0]),
        RegionOut(**region_documents[1]),
    ])

    p.assert_called_once_with(DB_DEP_MOCK)


def test_create_region_201(admin_api_client, mocker):
    region_doc = RegionFactory()
    p = mocker.patch('dbaas.webapp.Region.create', return_value=region_doc)

    response = admin_api_client.post(REGION_API, json=region_doc)
    assert response.status_code == 201
    assert response.json() == jsonable_encoder(RegionOut(**region_doc))

    p.assert_called_once_with(region_doc, db=DB_DEP_MOCK)


def test_create_region_400(admin_api_client, mocker):
    def raise_ve(*a, **kw):
        raise ValueError('fail')

    region_doc = RegionFactory()
    p = mocker.patch('dbaas.webapp.Region.create', side_effect=raise_ve)

    response = admin_api_client.post(REGION_API, json=region_doc)
    assert response.status_code == 400
    assert response.json() == {'message': 'fail'}

    p.assert_called_once_with(region_doc, db=DB_DEP_MOCK)


def test_create_region_403(api_client, mocker):
    region_doc = RegionFactory()
    p = mocker.patch('dbaas.webapp.Region.create')

    response = api_client.post('/api/v1/regions', json=region_doc)
    assert response.status_code == 403
    assert response.json() == {'message': 'Permission denied.'}

    p.assert_not_called()
