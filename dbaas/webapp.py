# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from logging import LoggerAdapter

from connect.eaas.core.decorators import (
    devops_pages,
    router,
    web_app,
)
from connect.eaas.core.extension import WebApplicationBase
from connect.eaas.core.inject.asynchronous import AsyncConnectClient
from connect.eaas.core.inject.common import get_call_context, get_config
from connect.eaas.core.inject.models import Context
from fastapi import Depends, responses

from dbaas.database import get_db, prepare_db
from dbaas.schemas import (
    DatabaseInCreate,
    DatabaseInUpdate,
    DatabaseOutDetail,
    DatabaseOutList,
    JsonError,
    RegionOut,
)
from dbaas.services import DB, Region
from dbaas.utils import get_installation_client


@web_app(router)
@devops_pages([{
    'label': 'Databases',
    'url': '/static/index.html',
}])
class DBaaSWebApplication(WebApplicationBase):

    @router.get(
        '/v1/databases',
        summary='List all databases',
        response_model=list[DatabaseOutList],
    )
    async def list_databases(
        self,
        context: Context = Depends(get_call_context),
        db=Depends(get_db),
    ):
        db_documents = await DB.list(db, context)

        return [DatabaseOutList(**db_doc) for db_doc in db_documents]

    @router.post(
        '/v1/databases',
        summary='Create database',
        response_model=DatabaseOutList,
        responses={400: {'model': JsonError}},
        status_code=201,
    )
    async def create_database(
        self,
        data: DatabaseInCreate,
        context: Context = Depends(get_call_context),
        client: AsyncConnectClient = Depends(get_installation_client),
        config: dict = Depends(get_config),
        db=Depends(get_db),
    ):
        try:
            db_document = await DB.create(
                data.dict(), db=db, context=context, client=client, config=config,
            )
        except ValueError as e:
            return self._service_logic_error_response(e)

        return DatabaseOutList(**db_document)

    @router.get(
        '/v1/databases/{db_id}',
        summary='Retrieve database',
        response_model=DatabaseOutDetail,
        responses={404: {'model': JsonError}},
    )
    async def retrieve_database(
        self,
        db_id: str,
        context: Context = Depends(get_call_context),
        db=Depends(get_db),
    ):
        db_document = await DB.retrieve(db_id, db, context)
        if not db_document:
            return self._db_not_found_response()

        return DatabaseOutDetail(**db_document)

    @router.put(
        '/v1/databases/{db_id}',
        summary='Update database',
        response_model=DatabaseOutDetail,
        responses={
            400: {'model': JsonError},
            404: {'model': JsonError},
        },
    )
    async def update_database(
        self,
        db_id: str,
        data: DatabaseInUpdate,
        context: Context = Depends(get_call_context),
        client: AsyncConnectClient = Depends(get_installation_client),
        db=Depends(get_db),
    ):
        db_document = await DB.retrieve(db_id, db, context)
        if not db_document:
            return self._db_not_found_response()

        try:
            updated_db_document = await DB.update(
                db_document,
                data.dict(),
                db=db,
                context=context,
                client=client,
            )
        except ValueError as e:
            return self._service_logic_error_response(e)

        return DatabaseOutDetail(**updated_db_document)

    @staticmethod
    def _db_not_found_response():
        return responses.JSONResponse({'message': 'Database not found.'}, status_code=404)

    @staticmethod
    def _service_logic_error_response(e: ValueError):
        return responses.JSONResponse({'message': str(e)}, status_code=400)

    @router.get(
        '/v1/regions',
        summary='List all regions',
        response_model=list[RegionOut],
    )
    async def list_regions(
        self,
        db=Depends(get_db),
    ):
        region_documents = await Region.list(db)
        return [RegionOut(**region_doc) for region_doc in region_documents]

    @classmethod
    async def on_startup(cls, logger: LoggerAdapter, config: dict):
        await prepare_db(logger, config)
