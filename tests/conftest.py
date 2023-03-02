# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from connect.client import AsyncConnectClient, ConnectClient

from dbaas.database import Collections, get_db, prepare_db
from dbaas.webapp import DBaaSWebApplication


@pytest.fixture
def connect_client():
    return ConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://localhost/public/v1',
    )


@pytest.fixture
def async_connect_client():
    return AsyncConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://localhost/public/v1',
    )


@pytest.fixture
def logger(mocker):
    return mocker.MagicMock()


@pytest.fixture
def config():
    return {
        'DB_HOST': 'db_ram',
        'DB_USER': 'root',
        'DB_PASSWORD': '1q2w3e',
        'DB_NAME': 'db',
    }


@pytest.fixture()
async def db(logger, config, mocker):
    mocker.patch(
        'dbaas.database.get_full_connection_string',
        side_effect=lambda conn_str: f'mongodb://{conn_str}/',
    )

    db = await prepare_db(logger, config)
    yield db

    for collection in (Collections.DB, Collections.REGION):
        db[collection].delete_many()


@pytest.fixture()
def api_client(test_client_factory):
    client = test_client_factory(DBaaSWebApplication)
    client.app.dependency_overrides = {
        get_db: lambda: 'db',
        prepare_db: lambda: None,
    }

    yield client
