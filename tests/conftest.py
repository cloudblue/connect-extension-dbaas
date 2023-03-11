# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#
import os

import pytest
from connect.eaas.core.inject.common import get_call_context, get_config
from connect.eaas.core.inject.models import Context

from dbaas.constants import ContextCallTypes
from dbaas.database import Collections, DBEnvVar, get_db, prepare_db
from dbaas.utils import get_installation_client
from dbaas.webapp import DBaaSWebApplication

from tests.constants import CONTEXT_DEP_MOCK, DB_DEP_MOCK, INSTALLATION_CLIENT_DEP_MOCK


@pytest.fixture
def logger(mocker):
    return mocker.MagicMock()


@pytest.fixture
def config():
    return {
        DBEnvVar.HOST: os.environ.get('DB_HOST', 'db_ram'),
        DBEnvVar.USER: 'root',
        DBEnvVar.PASSWORD: '1q2w3e',
        DBEnvVar.DB: 'db',
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
def api_client(test_client_factory, config):
    client = test_client_factory(DBaaSWebApplication)
    client.app.dependency_overrides = {
        get_db: lambda: DB_DEP_MOCK,
        prepare_db: lambda: None,
        get_installation_client: lambda: INSTALLATION_CLIENT_DEP_MOCK,
        get_call_context: lambda: CONTEXT_DEP_MOCK,
        get_config: lambda: config,
    }

    yield client


@pytest.fixture()
def admin_context():
    return Context(call_type=ContextCallTypes.ADMIN)
