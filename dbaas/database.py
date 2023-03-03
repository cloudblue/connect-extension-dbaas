# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import urllib
from logging import LoggerAdapter
from typing import Optional

from connect.eaas.core.inject.common import get_config
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
from pymongo.errors import CollectionInvalid


class Collections:
    DB = 'db'
    REGION = 'region'


class DBEnvVar:
    HOST = 'DB_HOST'
    USER = 'DB_USER'
    PASSWORD = 'DB_PASSWORD'
    DB = 'DB_NAME'


def get_db(config: dict = Depends(get_config)) -> AsyncIOMotorDatabase:
    db_host = config[DBEnvVar.HOST]
    db_user = urllib.parse.quote(config[DBEnvVar.USER])
    db_password = urllib.parse.quote(config[DBEnvVar.PASSWORD])

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
) -> Optional[AsyncIOMotorCollection]:
    coll_name = Collections.DB

    try:
        collection = await db.create_collection(coll_name)
        return collection

    except CollectionInvalid:
        _log_that_collection_exists(logger, coll_name)


async def prepare_region_collection(
    db: AsyncIOMotorDatabase,
    logger: LoggerAdapter,
) -> Optional[AsyncIOMotorCollection]:
    coll_name = Collections.REGION

    try:
        collection = await db.create_collection(coll_name)
        return collection

    except CollectionInvalid:
        _log_that_collection_exists(logger, coll_name)


def _log_that_collection_exists(logger: LoggerAdapter, coll_name: str):
    logger.info('Collection %s already exists.', coll_name)
