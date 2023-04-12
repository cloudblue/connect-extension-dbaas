# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#
import os

import pytest
from connect.client import AsyncConnectClient
from connect.eaas.core.inject.common import get_call_context, get_config
from connect.eaas.core.inject.models import Context

from dbaas.constants import ContextCallTypes
from dbaas.database import Collections, DBEnvVar, get_db, prepare_db
from dbaas.utils import get_installation_client
from dbaas.webapp import DBaaSWebApplication

from tests.constants import DB_DEP_MOCK, INSTALLATION_CLIENT_DEP_MOCK


@pytest.fixture
def default_endpoint():
    return 'https://localhost/public/v1'


@pytest.fixture
def logger(mocker):
    return mocker.MagicMock()


@pytest.fixture
def async_connect_client(default_endpoint, logger):
    return AsyncConnectClient(
        'ApiKey fake_api_key',
        endpoint=default_endpoint,
        logger=logger,
    )


@pytest.fixture
def async_client_mocker(async_client_mocker_factory, default_endpoint):
    return async_client_mocker_factory(base_url=default_endpoint)


@pytest.fixture
def config():
    return {
        DBEnvVar.HOST: os.environ.get('DB_HOST', 'db_ram'),
        DBEnvVar.USER: 'root',
        DBEnvVar.PASSWORD: '1q2w3e',
        DBEnvVar.DB: 'db',
        DBEnvVar.ENCRYPTION_KEY: '4e326a614b7653567337647176595555524552476f44'
                                 '55506b4d5048454b336b4c577851334c645f46634d3d',
    }


@pytest.fixture()
def patch_connection_string(mocker):
    mocker.patch(
        'dbaas.database.get_full_connection_string',
        side_effect=lambda conn_str: f'mongodb://{conn_str}/',
    )


@pytest.fixture()
async def db(logger, config, patch_connection_string):
    db = await prepare_db(logger, config)

    for collection in (Collections.DB, Collections.REGION):
        await db[collection].delete_many({})

    return db


@pytest.fixture()
def common_context():
    return Context(call_type=ContextCallTypes.USER)


@pytest.fixture()
def api_client(test_client_factory, config, common_context):
    client = test_client_factory(DBaaSWebApplication)
    client.app.dependency_overrides = {
        get_db: lambda: DB_DEP_MOCK,
        prepare_db: lambda: None,
        get_installation_client: lambda: INSTALLATION_CLIENT_DEP_MOCK,
        get_call_context: lambda: common_context,
        get_config: lambda: config,
    }

    yield client


@pytest.fixture()
def admin_context():
    return Context(call_type=ContextCallTypes.ADMIN)


@pytest.fixture()
def admin_api_client(api_client, admin_context):
    api_client.app.dependency_overrides[get_call_context] = lambda: admin_context

    yield api_client
