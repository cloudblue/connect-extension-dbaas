# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from copy import copy
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from connect.eaas.core.inject.models import Context

from dbaas.constants import DBStatus
from dbaas.database import Collections, list_all


class DB:
    COLLECTION = Collections.DB

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase, context: Context) -> list[dict]:
        db_coll = db[cls.COLLECTION]

        results = []
        for db_document in await list_all(db_coll, **cls._default_query(context)):
            doc = cls._modify_db_document(db_document)
            results.append(doc)

        return results

    @classmethod
    async def retrieve(
        cls,
        db_id: str,
        db: AsyncIOMotorDatabase,
        context: Context,
    ) -> Optional[dict]:
        db_coll = db[cls.COLLECTION]

        query = cls._default_query(context)
        query['id'] = {'$eq': db_id}
        db_document = db_coll.find_one(**query)

        if db_document:
            return cls._modify_db_document(db_document)

    @classmethod
    def _default_query(cls, context: Context) -> dict:
        return {
            'account_id': {'$eq': context.account_id},
            'status': {'$ne': DBStatus.DELETED},
        }

    @classmethod
    def _modify_db_document(cls, db_document: dict) -> dict:
        document = copy(db_document)

        cases = document.get('cases')
        if cases:
            document['case'] = cases[-1]

        return document


class Region:
    COLLECTION = Collections.REGION

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase) -> list[dict]:
        db_coll = db[cls.COLLECTION]

        results = await list_all(db_coll)
        return results
