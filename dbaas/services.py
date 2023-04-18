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

import bson
import pymongo
from connect.client import ClientError
from connect.eaas.core.logging import RequestLogger
from cryptography.fernet import Fernet
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from connect.eaas.core.inject.asynchronous import AsyncConnectClient, get_installation
from connect.eaas.core.inject.models import Context
from pymongo.errors import DuplicateKeyError, OperationFailure

from dbaas.constants import (
    DB_HELPDESK_CASE_DESCRIPTION_TPL,
    DB_HELPDESK_CASE_SUBJECT_TPL,
    DBAction,
    DBStatus,
)
from dbaas.database import Collections, DBEnvVar
from dbaas.utils import is_admin_context


class DB:
    COLLECTION = Collections.DB
    MAX_ID_GENERATION_RETRIES = 3
    LIST_STEP_LENGTH = 20

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase, context: Context) -> list[dict]:
        db_coll = db[cls.COLLECTION]
        cursor = db_coll.find(
            cls._default_query(context),
        ).sort('events.created.at', pymongo.DESCENDING)

        results = []

        docs = await cursor.to_list(length=cls.LIST_STEP_LENGTH)
        while docs:
            for db_document in docs:
                doc = cls._db_document_repr(db_document)
                results.append(doc)

            docs = await cursor.to_list(length=cls.LIST_STEP_LENGTH)

        return results

    @classmethod
    async def retrieve(
        cls,
        db_id: str,
        db: AsyncIOMotorDatabase,
        context: Context,
        config: Optional[dict] = None,
    ) -> Optional[dict]:
        db_coll = db[cls.COLLECTION]

        query = cls._default_query(context)
        query['id'] = db_id
        db_document = await db_coll.find_one(query)

        if db_document:
            return cls._db_document_repr(db_document, config=config)

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
    async def update(
        cls,
        db_document: dict,
        data: dict,
        db: AsyncIOMotorDatabase,
        context: Context,
        client: AsyncConnectClient,
        **kwargs,
    ) -> dict:
        updated_db_document = await cls._update(db_document, data, db, context, client)

        return cls._db_document_repr(updated_db_document)

    @classmethod
    async def delete(
        cls,
        db_document: dict,
        db: AsyncIOMotorDatabase,
        client: AsyncConnectClient,
        **kwargs,
    ) -> dict:
        updated_db_document = copy(db_document)
        updates = {'status': DBStatus.DELETED}

        updated_events = updated_db_document.get('events', {})
        updated_events['deleted'] = cls._prepare_event()
        updates['events'] = updated_events

        db_coll = db[cls.COLLECTION]
        await db_coll.update_one(
            {'id': db_document['id']},
            {'$set': updates},
        )
        updated_db_document.update(updates)

        cls._resolve_last_db_document_case(db_document, client)

        return cls._db_document_repr(updated_db_document)

    @classmethod
    async def reconfigure(
        cls,
        db_document: dict,
        data: dict,
        db: AsyncIOMotorDatabase,
        context: Context,
        client: AsyncConnectClient,
        **kwargs,
    ) -> dict:
        status = db_document.get('status')
        if status != DBStatus.ACTIVE:
            raise ValueError('Only active DB can be reconfigured.')

        actor = await cls._get_actor(context, client)
        db_document_id = db_document['id']

        updated_db_document = copy(db_document)
        updates = {'status': DBStatus.RECONFIGURING}

        updated_events = updated_db_document.get('events', {})
        updated_events['reconfigured'] = cls._prepare_event(actor)
        updates['events'] = updated_events

        if not is_admin_context(context):
            installation = await ConnectInstallation.retrieve(context.installation_id, client)

            description = data.get('details') or '-'
            helpdesk_case = await ConnectHelpdeskCase.create_from_db_document(
                db_document,
                action=data['action'],
                description=description,
                installation=installation,
                client=client,
            )

            cases = updated_db_document.get('cases', [])
            cases.append(cls._prepare_helpdesk_case(helpdesk_case))
            updates['cases'] = cases

        db_coll = db[cls.COLLECTION]
        await db_coll.update_one(
            {'id': db_document_id},
            {'$set': updates},
        )

        updated_db_document.update(updates)
        return cls._db_document_repr(updated_db_document)

    @classmethod
    async def activate(
        cls,
        db_document: dict,
        data: dict,
        db: AsyncIOMotorDatabase,
        config: dict,
        client: AsyncConnectClient,
        **kwargs,
    ) -> dict:
        updated_db_document = await cls._activate(db_document, data, db, config, client)

        return cls._db_document_repr(updated_db_document, config=config)

    @classmethod
    async def _activate(
        cls,
        db_document: dict,
        data: dict,
        db: AsyncIOMotorDatabase,
        config: dict,
        client: AsyncConnectClient,
    ):
        status = db_document.get('status')
        credentials = data.get('credentials')

        workload = data.get('workload')
        workload_is_updated = workload and workload != db_document.get('workload')

        updates = {'status': DBStatus.ACTIVE}

        if not credentials:
            if status == DBStatus.REVIEWING:
                raise ValueError('Credentials are required for DB activation.')

            if (not workload_is_updated) and status == DBStatus.ACTIVE:
                return db_document

        else:
            updates['credentials'] = cls._encrypt_dict(credentials, config)

        if workload_is_updated:
            updates['workload'] = workload

        updated_db_document = copy(db_document)
        updated_events = updated_db_document.get('events', {})
        updated_events['activated'] = cls._prepare_event()
        updates['events'] = updated_events

        db_coll = db[cls.COLLECTION]
        await db_coll.update_one(
            {'id': db_document['id']},
            {'$set': updates},
        )
        updated_db_document.update(updates)

        cls._resolve_last_db_document_case(db_document, client)

        return updated_db_document

    @classmethod
    async def _update(
        cls,
        db_document: dict,
        data: dict,
        db: AsyncIOMotorDatabase,
        context: Context,
        client: AsyncConnectClient,
    ) -> dict:
        if not data:
            return db_document

        updates = {}
        tech_contact_data = data.get('tech_contact')
        if tech_contact_data and tech_contact_data['id'] != db_document['tech_contact']['id']:
            tech_contact = await cls._get_validated_tech_contact(data, context, client)
            updates['tech_contact'] = cls._prepare_tech_contact(tech_contact)

        for key in ('name', 'description'):
            value = data.get(key)
            if value and value != db_document.get(key):
                updates[key] = value

        if not updates:
            return db_document

        actor = await cls._get_actor(context, client)

        updated_db_document = copy(db_document)
        updated_events = updated_db_document.get('events', {})
        updated_events['updated'] = cls._prepare_event(actor)
        updates['events'] = updated_events

        db_coll = db[cls.COLLECTION]
        await db_coll.update_one(
            {'id': db_document['id']},
            {'$set': updates},
        )

        updated_db_document.update(updates)
        return updated_db_document

    @classmethod
    def _resolve_last_db_document_case(cls, db_document: dict, client: AsyncConnectClient):
        case = cls._get_last_db_document_case(db_document)
        if case:
            asyncio.create_task(ConnectHelpdeskCase.resolve(case['id'], client))

    @classmethod
    def _default_query(cls, context: Context) -> dict:
        q = {'status': {'$ne': DBStatus.DELETED}}

        if not is_admin_context(context):
            q['account_id'] = context.account_id

        return q

    @classmethod
    def _db_document_repr(cls, db_document: dict, config: dict = None) -> dict:
        document = copy(db_document)
        document['owner'] = {'id': document.get('account_id')}

        case = cls._get_last_db_document_case(document)
        if case:
            document['case'] = case

        status = document.get('status')
        credentials = db_document.get('credentials')
        if credentials:
            if (not config) or (status not in (DBStatus.ACTIVE, DBStatus.RECONFIGURING)):
                del document['credentials']

            else:
                document['credentials'] = cls._decrypt_dict(document['credentials'], config)

        return document

    @classmethod
    def _get_last_db_document_case(cls, db_document: dict) -> Optional[dict]:
        cases = db_document.get('cases')
        return cases[-1] if cases else None

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
        db_document['events'] = {'created': cls._prepare_event(actor)}
        db_document['region'] = {
            'id': region_doc['id'],
            'name': region_doc['name'],
        }
        db_document['tech_contact'] = cls._prepare_tech_contact(tech_contact)

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
                    action=DBAction.CREATE,
                    description=db_document['description'],
                    installation=installation,
                    client=client,
                )

                db_document['cases'] = [cls._prepare_helpdesk_case(helpdesk_case)]

                db_coll = cls._db_collection_from_db_session(db_session, config)
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
        db_coll = cls._db_collection_from_db_session(db_session, config)

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
    def _db_collection_from_db_session(cls, db_session, config):
        return db_session.client[config[DBEnvVar.DB]][cls.COLLECTION]

    @staticmethod
    def _generate_id(config: dict) -> str:
        id_random_length = config.get('DB_ID_RANDOM_LENGTH', 5)
        id_prefix = config.get('DB_ID_PREFIX', 'DBPG')

        random_part = ''.join(random.choice(string.digits) for _ in range(id_random_length))
        return f'{id_prefix}-{random_part}'

    @staticmethod
    def _prepare_tech_contact(tech_contact: dict) -> dict:
        return {
            'id': tech_contact['id'],
            'name': tech_contact['name'],
            'email': tech_contact['email'],
        }

    @staticmethod
    def _prepare_helpdesk_case(helpdesk_case: dict) -> dict:
        return {'id': helpdesk_case['id']}

    @staticmethod
    def _prepare_event(actor: Optional[dict] = None) -> dict:
        result = {
            'at': datetime.now(tz=timezone.utc),
        }

        if actor:
            result['by'] = {
                'id': actor['id'],
                'name': actor['name'],
            }

        return result

    @classmethod
    def _decrypt_dict(cls, value: bytes, config: dict):
        decrypted_byte_value = Fernet(cls._crypto_key(config)).decrypt(value)

        return bson.decode(decrypted_byte_value)

    @classmethod
    def _encrypt_dict(cls, value, config: dict):
        byte_value = bson.encode(value)
        encrypted_byte_value = Fernet(cls._crypto_key(config)).encrypt(byte_value)

        return encrypted_byte_value

    @staticmethod
    def _crypto_key(config: dict):
        return bytes.fromhex(config[DBEnvVar.ENCRYPTION_KEY])


class Region:
    COLLECTION = Collections.REGION

    @classmethod
    async def list(cls, db: AsyncIOMotorDatabase) -> list[dict]:
        region_coll = db[cls.COLLECTION]
        results = await region_coll.find().sort('name').to_list(length=20)

        return results

    @classmethod
    async def retrieve(cls, region_id: str, db: AsyncIOMotorDatabase) -> Optional[dict]:
        region_coll = db[cls.COLLECTION]
        region_document = await region_coll.find_one({'id': region_id})

        return region_document

    @classmethod
    async def create(cls, data: dict, db: AsyncIOMotorDatabase) -> dict:
        region_coll = db[cls.COLLECTION]
        try:
            await region_coll.insert_one(data)
            return data

        except DuplicateKeyError:
            raise ValueError('ID must be unique.')


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
    HIGH_PRIORITY = 2
    TECHNICAL_TYPE = 'technical'

    @classmethod
    async def create_from_db_document(
        cls,
        db_document: dict,
        action: str,
        description: str,
        installation: dict,
        client: AsyncConnectClient,
    ) -> dict:
        db_id = db_document['id']
        db_name = db_document['name']
        contact_id = db_document['tech_contact']['id']

        subject = DB_HELPDESK_CASE_SUBJECT_TPL.format(
            db_id=db_id,
            db_name=db_name,
            action=action,
        )
        description = DB_HELPDESK_CASE_DESCRIPTION_TPL.format(
            db_id=db_id,
            db_name=db_name,
            db_workload=db_document['workload'],
            region_id=db_document['region']['id'],
            contact_id=contact_id,
            action=action,
            description=description,
        )

        data = {
            'subject': subject,
            'description': description,
            'priority': cls.HIGH_PRIORITY,
            'type': cls.TECHNICAL_TYPE,
            'issuer': {
                'recipients': [
                    {'id': contact_id},
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

    @classmethod
    async def resolve(cls, case_id: str, client: AsyncConnectClient):
        try:
            await client('helpdesk').cases[case_id]('resolve').post()
        except ClientError:
            client.logger.logger.warning('Could not resolve case %s.', case_id)
