# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#
import asyncio
import random
import string
from copy import copy
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from connect.eaas.core.inject.asynchronous import AsyncConnectClient, get_installation
from connect.eaas.core.inject.models import Context

from dbaas.constants import DBStatus
from dbaas.database import Collections


class DB:
    COLLECTION = Collections.DB

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase, context: Context) -> list[dict]:
        db_coll = db[cls.COLLECTION]
        cursor = db_coll.find(cls._default_query(context)).sort('events.created.at')

        results = []
        for db_document in await cursor.to_list(length=20):
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
        query['id'] = db_id
        db_document = await db_coll.find_one(query)

        if db_document:
            return cls._modify_db_document(db_document)

    @classmethod
    async def create(
        cls,
        data: dict,
        db: AsyncIOMotorDatabase,
        context: Context,
        client: AsyncConnectClient,
        config: dict,
    ) -> dict:
        region_id = data['region']['id']
        region_doc = await Region.retrieve(region_id, db)
        if not region_doc:
            raise ValueError('Region does not exist.')

        account_id = context.account_id
        tech_contact_id = data['tech_contact']['id']
        tech_contact = await client.accounts[account_id].users[tech_contact_id].get()
        if not tech_contact['active']:
            raise ValueError('Only active user can be a technical contact.')

        if tech_contact['blocklisted']:
            raise ValueError('Blocklisted user can not be a technical contact.')

        actor = tech_contact
        if tech_contact_id != context.user_id:
            actor = await client.accounts[account_id].users[context.user_id].get()

        db_document = copy(data)
        db_document['account_id'] = account_id
        db_document['status'] = DBStatus.REVIEWING
        db_document['events'] = {
            'created': {
                'at': datetime.now(tz=timezone.utc),
                'by': {
                    'id': actor['id'],
                    'name': actor['name'],
                },
            },
        }
        db_document['region'] = {
            'id': region_doc['id'],
            'name': region_doc['name'],
        }
        db_document['tech_contact'] = {
            'id': tech_contact['id'],
            'name': tech_contact['name'],
            'email': tech_contact['email'],
        }

        db_coll = db[cls.COLLECTION]
        db_document = await cls._insert_document(db_document, db_coll, config)

        # TODO: Think on that + Helpdesk part
        if context.call_type == 'admin':
            return db_document

        installation = await get_installation(
            client, x_connect_installation_id=context.installation_id,
        )
        helpdesk_case = await cls._create_helpdesk_case(db_document, installation, context, client)

        db_document['case'] = {'id': helpdesk_case['id']}
        asyncio.ensure_future(
            db_coll.update_one(
                {'id': db_document['id']},
                {'$set': {'cases': [db_document['case']]}},
            ),
        )

        return db_document

    @classmethod
    def _default_query(cls, context: Context) -> dict:
        return {
            'account_id': context.account_id,
            'status': {'$ne': DBStatus.DELETED},
        }

    @classmethod
    def _modify_db_document(cls, db_document: dict) -> dict:
        document = copy(db_document)

        cases = document.get('cases')
        if cases:
            document['case'] = cases[-1]

        status = document['status']
        if status not in (DBStatus.ACTIVE, DBStatus.RECONFIGURING) and 'credentials' in db_document:
            del document['credentials']

        return document

    @classmethod
    async def _insert_document(
        cls, db_document: dict, db_coll: AsyncIOMotorCollection, config: dict,
    ):
        # TODO: ID integrity
        db_document['id'] = cls._generate_id(config)
        await db_coll.insert_one(db_document)

        return db_document

    @staticmethod
    def _generate_id(config: dict) -> str:
        id_random_length = config.get('DB_ID_RANDOM_LENGTH', 5)
        id_prefix = config.get('DB_ID_PREFIX', 'DBPG')

        random_part = ''.join(random.choice(string.digits) for _ in range(id_random_length))
        return f'{id_prefix}-{random_part}'

    @classmethod
    async def _create_helpdesk_case(
        cls, db_document: dict, installation: dict, context: Context, client: AsyncConnectClient,
    ):
        db_id = db_document['id']
        action = 'create'

        payload = {
            'subject': f'Request to {action} {db_id}.',
            'description': db_document['description'],
            'priority': 2,
            'type': 'business',
            'issuer': {
                'recipients': [
                    {'id': context.user_id},
                ],
            },
            'receiver': {
                'account': {'id': installation['environment']['extension']['owner']['id']},
            },
        }

        helpdesk_case = await client('helpdesk').cases.create(payload=payload)
        return helpdesk_case


class Region:
    COLLECTION = Collections.REGION

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase) -> list[dict]:
        db_coll = db[cls.COLLECTION]
        results = await db_coll.find().sort('name').to_list(length=20)

        return results

    @classmethod
    async def retrieve(
        cls,
        region_id: str,
        db: AsyncIOMotorDatabase,
    ) -> Optional[dict]:
        # TODO: Test
        db_coll = db[cls.COLLECTION]
        region_document = await db_coll.find_one({'id': region_id})

        return region_document
