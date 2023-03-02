# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from fastapi.encoders import jsonable_encoder

from dbaas.schemas import DatabaseOutDetail, DatabaseOutList, RegionOut
from dbaas.webapp import DBaaSWebApplication

from tests.factories import DBFactory, RegionFactory
from tests.utils import ANYContext


@pytest.mark.asyncio
async def test_on_start(test_client_factory, config, mocker):
    p = mocker.patch('dbaas.webapp.prepare_db')

    await DBaaSWebApplication().on_startup(1, 2)

    p.assert_called_once_with(1, 2)


def test_list_databases_empty_list(api_client, mocker):
    p = mocker.patch('dbaas.webapp.DB.list', return_value=[])

    response = api_client.get('/api/v1/databases')
    assert response.status_code == 200
    assert response.json() == []

    p.assert_called_once_with('db', ANYContext)


def test_list_databases_several_results(api_client, mocker):
    db_documents = DBFactory.create_batch(2, account_id='VA-123')
    p = mocker.patch('dbaas.webapp.DB.list', return_value=db_documents)

    response = api_client.get('/api/v1/databases')
    assert response.status_code == 200
    assert response.json() == jsonable_encoder([
        DatabaseOutList(**db_documents[0]),
        DatabaseOutList(**db_documents[1]),
    ])

    p.assert_called_once_with('db', ANYContext)


def test_retrieve_database_200(api_client, mocker):
    db_document = DBFactory()
    p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=db_document)

    response = api_client.get('/api/v1/databases/DB-456-789')
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(DatabaseOutDetail(**db_document))

    p.assert_called_once_with('DB-456-789', 'db', ANYContext)


def test_retrieve_database_404(api_client, mocker):
    p = mocker.patch('dbaas.webapp.DB.retrieve', return_value=None)

    response = api_client.get('/api/v1/databases/DB-123')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Database not found'}

    p.assert_called_once_with('DB-123', 'db', ANYContext)


def test_list_regions(api_client, mocker):
    region_documents = RegionFactory.create_batch(2)
    p = mocker.patch('dbaas.webapp.Region.list', return_value=region_documents)

    response = api_client.get('/api/v1/regions')
    assert response.status_code == 200
    assert response.json() == jsonable_encoder([
        RegionOut(**region_documents[0]),
        RegionOut(**region_documents[1]),
    ])

    p.assert_called_once_with('db')
