import urllib

import motor.motor_asyncio
from connect.eaas.core.inject.common import get_config
from fastapi import Depends
from pymongo.errors import CollectionInvalid


def get_db(config: dict = Depends(get_config)):
    try:
        db_host = config['DB_HOST']
        db_user = urllib.parse.quote(config['DB_USER'])
        db_password = urllib.parse.quote(config['DB_PASSWORD'])

        connection_str = f'mongodb+srv://{db_user}:{db_password}@{db_host}/'
        client = motor.motor_asyncio.AsyncIOMotorClient(
            connection_str, serverSelectionTimeoutMS=5000,
        )

        return client[config['DB_NAME']]

    except KeyError:
        raise RuntimeError('DB is not configured!')


async def prepare_db(config: dict):
    db = get_db(config)

    try:
        await db.create_collection('db')
    except CollectionInvalid:
        pass

    try:
        await db.create_collection('region')
    except CollectionInvalid:
        pass


def list_all(db_collection, **filters):
    return db_collection.find(filters).to_list(length=1000)
