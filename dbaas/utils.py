# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from connect.eaas.core.inject.asynchronous import AsyncConnectClient, get_extension_client
from connect.eaas.core.inject.common import get_call_context
from connect.eaas.core.inject.models import Context
from fastapi import Depends

from dbaas.constants import ContextCallTypes


async def get_installation_client(
    context: Context = Depends(get_call_context),
    client: AsyncConnectClient = Depends(get_extension_client),
) -> AsyncConnectClient:
    data = (
        await client('devops')
        .services[context.extension_id]
        # diff between this and connect.eaas.core.inject.asynchronous.get_installation_admin_client
        .installations[context.installation_id]
        .action('impersonate')
        .post()
    )

    return AsyncConnectClient(
        data['installation_api_key'],
        endpoint=client.endpoint,
        default_headers=client.default_headers,
        logger=client.logger,
    )


def is_admin_context(context: Context) -> bool:
    return context.call_type == ContextCallTypes.ADMIN
