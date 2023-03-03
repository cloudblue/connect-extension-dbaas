# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import OperationFailure

from dbaas.database import (
    Collections,
    DBEnvVar,
    get_db,
    get_full_connection_string,
    prepare_db,
    prepare_db_collection,
    prepare_region_collection,
    validate_db_configuration,
)


@pytest.mark.asyncio
async def test_get_db_connected(config, patch_connection_string):
    db = get_db(config)
    assert isinstance(db, AsyncIOMotorDatabase)

    assert await db.client.server_info()


@pytest.mark.asyncio
async def test_get_db_connection_error(config, patch_connection_string):
    config[DBEnvVar.PASSWORD] = 'invalid'

    db = get_db(config)
    assert isinstance(db, AsyncIOMotorDatabase)

    with pytest.raises(OperationFailure):
        await db.client.server_info()


def test_get_full_connection_string():
    assert get_full_connection_string('host') == 'mongodb+srv://host/'


def test_validate_db_configuration_is_valid(config):
    assert validate_db_configuration(config) is None


@pytest.mark.parametrize('missing_var, error', (
    (DBEnvVar.HOST, 'DB is not configured! DB_HOST is missing.'),
    (DBEnvVar.DB, 'DB is not configured! DB_NAME is missing.'),
))
def test_validate_db_configuration_is_invalid(config, missing_var, error):
    del config[missing_var]

    with pytest.raises(RuntimeError) as e:
        validate_db_configuration(config)

    assert str(e.value) == error


@pytest.mark.asyncio
async def test_prepare_db(mocker):
    validation_p = mocker.patch('dbaas.database.validate_db_configuration')
    get_db_p = mocker.patch('dbaas.database.get_db', return_value='db')
    db_collection_p = mocker.patch('dbaas.database.prepare_db_collection')
    region_collection_p = mocker.patch('dbaas.database.prepare_region_collection')

    db = await prepare_db('logger', 'config')
    assert db == 'db'

    validation_p.assert_called_once_with('config')
    get_db_p.assert_called_once_with('config')
    db_collection_p.assert_called_once_with('db', 'logger')
    region_collection_p.assert_called_once_with('db', 'logger')


@pytest.mark.asyncio
async def test_prepare_db_collection_is_created(config, patch_connection_string):
    db_name = config[DBEnvVar.DB]
    coll_name = Collections.DB

    db = get_db(config)
    await db.drop_collection(coll_name)

    collection = await prepare_db_collection(db, None)
    assert collection.full_name == f'{db_name}.{coll_name}'


@pytest.mark.asyncio
async def test_prepare_db_collection_exists(db, logger):
    logger.reset_mock()

    result = await prepare_db_collection(db, logger)
    assert result is None

    logger.info.assert_called_once_with('Collection %s already exists.', Collections.DB)


@pytest.mark.asyncio
async def test_prepare_region_collection_is_created(config, patch_connection_string):
    db_name = config[DBEnvVar.DB]
    coll_name = Collections.REGION

    db = get_db(config)
    await db.drop_collection(coll_name)

    collection = await prepare_region_collection(db, None)
    assert collection.full_name == f'{db_name}.{coll_name}'


@pytest.mark.asyncio
async def test_prepare_region_collection_exists(db, logger):
    logger.reset_mock()

    result = await prepare_region_collection(db, logger)
    assert result is None

    logger.info.assert_called_once_with('Collection %s already exists.', Collections.REGION)
