# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import urllib
from logging import LoggerAdapter

from connect.eaas.core.inject.common import get_config
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo.errors import CollectionInvalid, PyMongoError


DBException = PyMongoError


class Collections:
    DB = 'db'
    REGION = 'region'


class DBEnvVar:
    HOST = 'DB_HOST'
    """ `DB_HOST` - MongoDB location accessible from Connect platform, e.x. `c0.x.mongodb.net` """

    DB = 'DB_NAME'
    """ `DB_NAME` - MongoDB DB name, to store the data of this extension, e.x. `db` """

    USER = 'DB_USER'
    """ `DB_USER` - MongoDB username with read and write access to the `DB_NAME`, e.x. `dev` """

    PASSWORD = 'DB_PASSWORD'
    """ `DB_PASSWORD` - MongoDB user password from the MongoDB `DB_USER` """

    ENCRYPTION_KEY = 'DB_ENCRYPTION_KEY'
    """
    `DB_ENCRYPTION_KEY` - Client Encryption/Decryption secret string

    ```python
    # pip install cryptography

    from cryptography import fernet
    DB_ENCRYPTION_KEY = fernet.Fernet.generate_key().hex()
    ```
    """


def get_db(config: dict = Depends(get_config)) -> AsyncIOMotorDatabase:
    db_host = config[DBEnvVar.HOST]
    db_user = urllib.parse.quote(config[DBEnvVar.USER])
    db_password = urllib.parse.quote(config[DBEnvVar.PASSWORD])

    assert config[DBEnvVar.ENCRYPTION_KEY]

    connection_str = get_full_connection_string(f'{db_user}:{db_password}@{db_host}')
    client = AsyncIOMotorClient(connection_str, serverSelectionTimeoutMS=5000)

    return client[config[DBEnvVar.DB]]


def get_full_connection_string(conn_str: str) -> str:
    return f'mongodb+srv://{conn_str}/'


async def prepare_db(logger: LoggerAdapter, config: dict) -> AsyncIOMotorDatabase:
    validate_db_configuration(config)
    db = get_db(config)

    await prepare_db_collection(db, logger)
    await prepare_region_collection(db, logger)

    return db


def validate_db_configuration(config: dict):
    for var in (DBEnvVar.HOST, DBEnvVar.USER, DBEnvVar.PASSWORD, DBEnvVar.DB):
        if not config.get(var):
            raise RuntimeError(f'DB is not configured! {var} is missing.')


async def prepare_db_collection(
    db: AsyncIOMotorDatabase,
    logger: LoggerAdapter,
) -> AsyncIOMotorCollection:
    coll_name = Collections.DB

    try:
        collection = await db.create_collection(coll_name)

    except CollectionInvalid:
        _log_that_collection_exists(logger, coll_name)
        collection = db[coll_name]

    await collection.create_index('id', unique=True)

    return collection


async def prepare_region_collection(
    db: AsyncIOMotorDatabase,
    logger: LoggerAdapter,
) -> AsyncIOMotorCollection:
    coll_name = Collections.REGION

    try:
        collection = await db.create_collection(coll_name)

    except CollectionInvalid:
        _log_that_collection_exists(logger, coll_name)
        collection = db[coll_name]

    await collection.create_index('id', unique=True)

    return collection


def _log_that_collection_exists(logger: LoggerAdapter, coll_name: str):
    logger.info('Collection %s already exists.', coll_name)
