# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from fastapi.encoders import jsonable_encoder

from dbaas.schemas import DatabaseIn, DatabaseOutDetail, DatabaseOutList, RegionOut
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
    data = DatabaseIn(**db_document).dict()

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
        DatabaseIn(**data).dict(),
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
