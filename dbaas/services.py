# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import random
import string
from copy import copy
from datetime import datetime, timezone
from typing import Optional

import pymongo
from connect.client import ClientError
from connect.eaas.core.logging import RequestLogger
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from connect.eaas.core.inject.asynchronous import AsyncConnectClient, get_installation
from connect.eaas.core.inject.models import Context
from pymongo.errors import DuplicateKeyError, OperationFailure

from dbaas.constants import DBStatus, HelpdeskCaseSubjectAction
from dbaas.database import Collections
from dbaas.utils import is_admin_context


class DB:
    COLLECTION = Collections.DB
    MAX_ID_GENERATION_RETRIES = 3

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase, context: Context) -> list[dict]:
        db_coll = db[cls.COLLECTION]
        cursor = db_coll.find(
            cls._default_query(context),
        ).sort('events.created.at', pymongo.DESCENDING)

        results = []
        for db_document in await cursor.to_list(length=20):
            doc = cls._db_document_repr(db_document)
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
            return cls._db_document_repr(db_document)

    @classmethod
    async def create(
        cls,
        data: dict,
        db: AsyncIOMotorDatabase,
        context: Context,
        client: AsyncConnectClient,
        config: dict,
    ) -> dict:
        region_doc = await cls._get_validated_region_document(data, db)
        tech_contact = await cls._get_validated_tech_contact(data, context, client)

        actor = tech_contact
        if tech_contact['id'] != context.user_id:
            actor = await cls._get_actor(context, client)

        prepared_db_doc = cls._prepare_db_document(data, context, region_doc, tech_contact, actor)
        inserted_db_doc = await cls._create_db_document(
            prepared_db_doc, db, context, client, config,
        )

        return cls._db_document_repr(inserted_db_doc)

    @classmethod
    def _default_query(cls, context: Context) -> dict:
        q = {'status': {'$ne': DBStatus.DELETED}}

        if not is_admin_context(context):
            q['account_id'] = context.account_id

        return q

    @classmethod
    def _db_document_repr(cls, db_document: dict) -> dict:
        document = copy(db_document)

        cases = document.get('cases')
        if cases:
            document['case'] = cases[-1]

        status = document.get('status')
        if status not in (DBStatus.ACTIVE, DBStatus.RECONFIGURING) and 'credentials' in db_document:
            del document['credentials']

        return document

    @classmethod
    async def _get_validated_region_document(
        cls,
        data: dict,
        db: AsyncIOMotorDatabase,
    ) -> dict:
        region_id = data['region']['id']
        region_doc = await Region.retrieve(region_id, db)
        if not region_doc:
            raise ValueError('Region does not exist.')

        return region_doc

    @classmethod
    async def _get_validated_tech_contact(
        cls,
        data: dict,
        context: Context,
        client: AsyncConnectClient,
    ) -> dict:
        account_id = context.account_id
        tech_contact_id = data['tech_contact']['id']

        tech_contact = await ConnectAccountUser.retrieve(account_id, tech_contact_id, client)
        if not tech_contact.get('active'):
            raise ValueError('Only active user can be a technical contact.')

        return tech_contact

    @classmethod
    async def _get_actor(cls, context: Context, client: AsyncConnectClient) -> dict:
        actor = await ConnectAccountUser.retrieve(context.account_id, context.user_id, client)

        return actor

    @classmethod
    def _prepare_db_document(
        cls,
        data: dict,
        context: Context,
        region_doc: dict,
        tech_contact: dict,
        actor: dict,
    ) -> dict:
        db_document = copy(data)
        db_document['account_id'] = context.account_id
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

        return db_document

    @classmethod
    async def _create_db_document(
        cls,
        db_document: dict,
        db: AsyncIOMotorDatabase,
        context: Context,
        client: AsyncConnectClient,
        config: dict,
    ) -> dict:
        is_admin_ctx = is_admin_context(context)
        installation = None
        if not is_admin_ctx:
            installation = await ConnectInstallation.retrieve(context.installation_id, client)

        async with await db.client.start_session() as db_session:
            async with db_session.start_transaction():
                db_document = await cls._create_db_document_in_db(
                    db_document, db_session, config, client.logger,
                )

                if is_admin_ctx:
                    return db_document

                helpdesk_case = await ConnectHelpdeskCase.create_from_db_document(
                    db_document,
                    action=HelpdeskCaseSubjectAction.CREATE,
                    description=db_document['description'],
                    installation=installation,
                    client=client,
                )

                db_document['cases'] = [{'id': helpdesk_case['id']}]

                db_coll = cls._db_collection_from_db_session(db_session)
                await db_coll.update_one(
                    {'id': db_document['id']},
                    {'$set': {'cases': db_document['cases']}},
                    session=db_session,
                )

                return db_document

    @classmethod
    async def _create_db_document_in_db(
        cls,
        db_document: dict,
        db_session: AsyncIOMotorCollection,
        config: dict,
        logger: RequestLogger,
        iteration: int = 0,
    ):
        db_coll = cls._db_collection_from_db_session(db_session)

        try:
            db_document['id'] = cls._generate_id(config)
            await db_coll.insert_one(db_document, session=db_session)

        except DuplicateKeyError:
            next_iteration = iteration + 1
            if next_iteration == cls.MAX_ID_GENERATION_RETRIES:
                raise ValueError('ID generation error.')

            logger.logger.warning('ID regeneration attempt %d...', next_iteration)
            db_document = await cls._create_db_document_in_db(
                db_document, db_session, config, logger, next_iteration,
            )

        except OperationFailure:
            logger.logger.exception('DB writing error.')
            raise ClientError(status_code=503)

        return db_document

    @classmethod
    def _db_collection_from_db_session(cls, db_session):
        return db_session.client.db[cls.COLLECTION]

    @staticmethod
    def _generate_id(config: dict) -> str:
        id_random_length = config.get('DB_ID_RANDOM_LENGTH', 5)
        id_prefix = config.get('DB_ID_PREFIX', 'DBPG')

        random_part = ''.join(random.choice(string.digits) for _ in range(id_random_length))
        return f'{id_prefix}-{random_part}'


class Region:
    COLLECTION = Collections.REGION

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase) -> list[dict]:
        db_coll = db[cls.COLLECTION]
        results = await db_coll.find().sort('name').to_list(length=20)

        return results

    @classmethod
    async def retrieve(cls, region_id: str, db: AsyncIOMotorDatabase) -> Optional[dict]:
        db_coll = db[cls.COLLECTION]
        region_document = await db_coll.find_one({'id': region_id})

        return region_document


class ConnectAccountUser:
    @classmethod
    async def retrieve(
        cls,
        account_id: str,
        user_id: str,
        client: AsyncConnectClient,
    ) -> Optional[dict]:
        user = await client.accounts[account_id].users[user_id].get()

        return user


class ConnectInstallation:
    @classmethod
    async def retrieve(cls, installation_id: str, client: AsyncConnectClient) -> dict:
        installation = await get_installation(
            client, x_connect_installation_id=installation_id,
        )
        cls.get_extension_owner_id(installation)

        return installation

    @staticmethod
    def get_extension_owner_id(installation: dict) -> str:
        try:
            return installation['environment']['extension']['owner']['id']

        except KeyError:
            raise ClientError(status_code=500)


class ConnectHelpdeskCase:
    @classmethod
    async def create_from_db_document(
        cls,
        db_document: dict,
        action: str,
        description: str,
        installation: str,
        client: AsyncConnectClient,
    ) -> dict:
        db_id = db_document['id']

        data = {
            'subject': f'Request to {action} {db_id}.',
            'description': description,
            'priority': 2,  # high
            'type': 'business',
            'issuer': {
                'recipients': [
                    {'id': db_document['tech_contact']['id']},
                ],
            },
            'receiver': {
                'account': {'id': ConnectInstallation.get_extension_owner_id(installation)},
            },
        }

        helpdesk_case = await cls.create(data, client)

        return helpdesk_case

    @classmethod
    async def create(
        cls,
        data: dict,
        client: AsyncConnectClient,
    ) -> dict:
        helpdesk_case = await client('helpdesk').cases.create(payload=data)

        return helpdesk_case
