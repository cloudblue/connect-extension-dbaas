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
from pymongo.errors import CollectionInvalid


class Collections:
    DB = 'db'
    REGION = 'region'


def get_db(config: dict = Depends(get_config)) -> AsyncIOMotorDatabase:
    try:
        db_host = config['DB_HOST']
        db_user = urllib.parse.quote(config['DB_USER'])
        db_password = urllib.parse.quote(config['DB_PASSWORD'])

        connection_str = get_full_connection_string(f'{db_user}:{db_password}@{db_host}')
        client = AsyncIOMotorClient(connection_str, serverSelectionTimeoutMS=5000)

        return client[config['DB_NAME']]

    except KeyError:
        raise RuntimeError('DB is not configured!')


def get_full_connection_string(conn_str: str) -> str:
    return f'mongodb+srv://{conn_str}/'


async def prepare_db(logger: LoggerAdapter, config: dict) -> AsyncIOMotorDatabase:
    db = get_db(config)
    coll_exists_info = 'Collection %s already exists.'

    try:
        await db.create_collection(Collections.DB)
    except CollectionInvalid:
        logger.info(coll_exists_info, Collections.DB)

    try:
        await db.create_collection(Collections.REGION)
    except CollectionInvalid:
        logger.info(coll_exists_info, Collections.DB)

    return db


def list_all(db_collection: AsyncIOMotorCollection, **filters) -> list[dict]:
    return db_collection.find(filters).to_list(length=1000)
