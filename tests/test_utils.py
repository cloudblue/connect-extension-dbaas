# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, CloudBlue
# All rights reserved.
#

import pytest
from connect.client import AsyncConnectClient
from connect.eaas.core.inject.models import Context

from dbaas.utils import get_installation_client, is_admin_context


@pytest.mark.asyncio
async def test_get_installation_client(async_client_mocker_factory, logger):
    client_mocker = async_client_mocker_factory(base_url='https://localhost/public/v1')

    ctx = Context(extension_id='SRVC-000', installation_id='EIN-123')
    client_mocker(
        'devops',
    ).services['SRVC-000'].installations['EIN-123'].action(
        'impersonate',
    ).post(
        return_value={'installation_api_key': 'my_inst_api_key'},
    )

    extension_client = AsyncConnectClient(
        'api_key',
        endpoint='https://localhost/public/v1',
        default_headers={'A': 'B'},
        logger=logger,
        use_specs=False,
    )

    installation_admin_client = await get_installation_client(
        ctx, extension_client,
    )

    assert isinstance(installation_admin_client, AsyncConnectClient)
    assert installation_admin_client.api_key == 'my_inst_api_key'
    assert installation_admin_client.endpoint == extension_client.endpoint
    assert installation_admin_client.default_headers == extension_client.default_headers
    assert installation_admin_client.logger == extension_client.logger


@pytest.mark.parametrize('call_type, is_admin', (('admin', True), ('user', False)))
def test_is_admin_context(call_type, is_admin):
    assert is_admin_context(Context(call_type=call_type)) is is_admin
