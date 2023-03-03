# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#
import os

import pytest

from dbaas.database import Collections, DBEnvVar, get_db, prepare_db
from dbaas.webapp import DBaaSWebApplication


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
def api_client(test_client_factory):
    client = test_client_factory(DBaaSWebApplication)
    client.app.dependency_overrides = {
        get_db: lambda: 'db',
        prepare_db: lambda: None,
    }

    yield client
