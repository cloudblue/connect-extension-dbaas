# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from connect.client import ClientError

from dbaas.services import ConnectAccountUser

from tests.factories import UserFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('status_code', (404, 503))
async def test_retrieve_bad_response_from_connect_api(
    async_client_mocker, status_code, async_connect_client,
):
    async_client_mocker.accounts['PA-123'].users['UR-456'].get(status_code=status_code)

    with pytest.raises(ClientError):
        await ConnectAccountUser.retrieve('VA-123', 'UR-456', async_connect_client)


@pytest.mark.asyncio
async def test_retrieve_ok(async_client_mocker, async_connect_client):
    user = UserFactory()

    async_client_mocker.accounts['PA-123'].users[user['id']].get(return_value=user)

    result = await ConnectAccountUser.retrieve('PA-123', user['id'], async_connect_client)

    assert result == user
