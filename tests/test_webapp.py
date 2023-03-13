# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from fastapi.encoders import jsonable_encoder

from dbaas.schemas import (
    DatabaseInCreate,
    DatabaseInUpdate,
    DatabaseOutDetail,
    DatabaseOutList,
    RegionOut,
)
from dbaas.webapp import DBaaSWebApplication

from tests.constants import CONTEXT_DEP_MOCK, DB_DEP_MOCK, INSTALLATION_CLIENT_DEP_MOCK
from tests.factories import DBFactory, RegionFactory


@pytest.mark.asyncio
async def test_on_start(mocker):
    p = mocker.patch('dbaas.webapp.prepare_db')

    await DBaaSWebApplication().on_startup(1, 2)

    p.assert_called_once_with(1, 2)


def test_list_databases_is_empty(api_client, mocker):
    p = mocker.patch('dbaas.webapp.DB.list', return_value=[])

    response = api_client.get('/api/v1/databases')
    assert response.status_code == 200
    assert response.json() == []

    p.assert_called_once_with(DB_DEP_MOCK, CONTEXT_DEP_MOCK)


def test_list_databases_several_dbs(api_client, mocker):
    db_documents = DBFactory.create_batch(2, account_id='VA-123')
    p = mocker.patch('dbaas.webapp.DB.list', return_value=db_documents)

    response = api_client.get('/api/v1/databases')
    assert response.status_code == 200
    assert response.json() == jsonable_encoder([
        DatabaseOutList(**db_documents[0]),
        DatabaseOutList(**db_documents[1]),
    ])

    p.assert_called_once_with(DB_DEP_MOCK, CONTEXT_DEP_MOCK)


def test_retrieve_database_200(api_client, mocker):
    db_document = DBFactory()
    p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=db_document)

    response = api_client.get('/api/v1/databases/DB-456-789')
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    p.assert_called_once_with('DB-456-789', DB_DEP_MOCK, CONTEXT_DEP_MOCK)


def test_retrieve_database_404(api_client, mocker):
    p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)

    response = api_client.get('/api/v1/databases/DB-123')
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    p.assert_called_once_with('DB-123', DB_DEP_MOCK, CONTEXT_DEP_MOCK)


def test_create_database_201(api_client, mocker, config):
    db_document = DBFactory()
    p = mocker.patch('dbaas.webapp.DB.create', return_value=db_document)
    data = DatabaseInCreate(**db_document).dict()

    response = api_client.post('/api/v1/databases', json=data)
    assert response.status_code == 201
    assert response.json() == jsonable_encoder(DatabaseOutList(**db_document))

    p.assert_called_once_with(
        data,
        db=DB_DEP_MOCK,
        context=CONTEXT_DEP_MOCK,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=config,
    )


def test_create_database_400(api_client, mocker, config):
    def raise_ve(*a, **kw):
        raise ValueError('test')

    p = mocker.patch('dbaas.webapp.DB.create', side_effect=raise_ve)
    data = DBFactory(events=None)

    response = api_client.post('/api/v1/databases', json=data)
    assert response.status_code == 400
    assert response.json() == {'message': 'test'}

    p.assert_called_once_with(
        DatabaseInCreate(**data).dict(),
        db=DB_DEP_MOCK,
        context=CONTEXT_DEP_MOCK,
        client=INSTALLATION_CLIENT_DEP_MOCK,
        config=config,
    )


def test_create_database_422(api_client, mocker):
    p = mocker.patch('dbaas.webapp.DB.create')
    data = {'invalid': 'data'}

    response = api_client.post('/api/v1/databases', json=data)
    assert response.status_code == 422
    assert response.json()

    p.assert_not_called()


def test_update_database_200(api_client, mocker, config):
    db_document = DBFactory()
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'a': True})
    update_p = mocker.patch('dbaas.webapp.DB.update', return_value=db_document)
    data = DatabaseInUpdate(**db_document).dict()

    response = api_client.put(f'/api/v1/databases/{db_document_id}', json=data)
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, CONTEXT_DEP_MOCK)
    update_p.assert_called_once_with(
        {'a': True},
        data,
        db=DB_DEP_MOCK,
        context=CONTEXT_DEP_MOCK,
        client=INSTALLATION_CLIENT_DEP_MOCK,
    )


def test_update_database_400(api_client, mocker, config):
    def raise_ve(*a, **kw):
        raise ValueError('test1')

    db_document = DBFactory(events=None)
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'some': 'mock'})
    update_p = mocker.patch('dbaas.webapp.DB.update', side_effect=raise_ve)
    data = DatabaseInUpdate(**db_document).dict()

    response = api_client.put(f'/api/v1/databases/{db_document_id}', json=data)
    assert response.status_code == 400
    assert response.json() == {'message': 'test1'}

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, CONTEXT_DEP_MOCK)
    update_p.assert_called_once_with(
        {'some': 'mock'},
        data,
        db=DB_DEP_MOCK,
        context=CONTEXT_DEP_MOCK,
        client=INSTALLATION_CLIENT_DEP_MOCK,
    )


def test_update_database_404(api_client, mocker, config):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)
    update_p = mocker.patch('dbaas.webapp.DB.update')

    response = api_client.put('/api/v1/databases/DB-123', json={})
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    retrieve_p.assert_called_once_with('DB-123', DB_DEP_MOCK, CONTEXT_DEP_MOCK)
    update_p.assert_not_called()


def test_update_database_422(api_client, mocker, config):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve')
    update_p = mocker.patch('dbaas.webapp.DB.update')

    response = api_client.put('/api/v1/databases/DB-456', json={'name': {}})
    assert response.status_code == 422
    assert response.json()

    retrieve_p.assert_not_called()
    update_p.assert_not_called()


def test_reconfigure_database_200(api_client, mocker, config):
    db_document = DBFactory()
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'b': True})
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure', return_value=db_document)
    data = {'case': {'subject': 'Reconf', 'description': None}}

    response = api_client.post(f'/api/v1/databases/{db_document_id}/reconfigure', json=data)
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, CONTEXT_DEP_MOCK)
    reconfigure_p.assert_called_once_with(
        {'b': True},
        data,
        db=DB_DEP_MOCK,
        context=CONTEXT_DEP_MOCK,
        client=INSTALLATION_CLIENT_DEP_MOCK,
    )


def test_reconfigure_database_400(api_client, mocker, config):
    def raise_ve(*a, **kw):
        raise ValueError('test2')

    db_document = DBFactory(events=None)
    db_document_id = db_document['id']
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value={'some': 'mock'})
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure', side_effect=raise_ve)
    data = {'case': {'subject': 'Reconf', 'description': 'x'}}

    response = api_client.post(f'/api/v1/databases/{db_document_id}/reconfigure', json=data)
    assert response.status_code == 400
    assert response.json() == {'message': 'test2'}

    retrieve_p.assert_called_once_with(db_document_id, DB_DEP_MOCK, CONTEXT_DEP_MOCK)
    reconfigure_p.assert_called_once_with(
        {'some': 'mock'},
        data,
        db=DB_DEP_MOCK,
        context=CONTEXT_DEP_MOCK,
        client=INSTALLATION_CLIENT_DEP_MOCK,
    )


def test_reconfigure_database_404(api_client, mocker, config):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure')
    data = {'case': {'subject': 'test'}}

    response = api_client.post('/api/v1/databases/DB-789/reconfigure', json=data)
    assert response.status_code == 404
    assert response.json() == {'message': 'Database not found.'}

    retrieve_p.assert_called_once_with('DB-789', DB_DEP_MOCK, CONTEXT_DEP_MOCK)
    reconfigure_p.assert_not_called()


def test_reconfigure_database_422(api_client, mocker, config):
    retrieve_p = mocker.patch('dbaas.webapp.DB.retrieve')
    reconfigure_p = mocker.patch('dbaas.webapp.DB.reconfigure')

    response = api_client.post('/api/v1/databases/DB-456/reconfigure', json={'case': None})
    assert response.status_code == 422
    assert response.json()

    retrieve_p.assert_not_called()
    reconfigure_p.assert_not_called()


def test_list_regions(api_client, mocker):
    region_documents = RegionFactory.create_batch(2)
    p = mocker.patch('dbaas.webapp.Region.list', return_value=region_documents)

    response = api_client.get('/api/v1/regions')
    assert response.status_code == 200
    assert response.json() == jsonable_encoder([
        RegionOut(**region_documents[0]),
        RegionOut(**region_documents[1]),
    ])

    p.assert_called_once_with(DB_DEP_MOCK)
