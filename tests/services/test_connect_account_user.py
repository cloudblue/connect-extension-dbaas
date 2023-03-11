# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from unittest.mock import AsyncMock

import pytest
from connect.client import ClientError

from dbaas.services import ConnectAccountUser

from tests.factories import UserFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('status_code', (404, 503))
async def test_retrieve_bad_response_from_connect_api(
    async_client_mocker_factory, mocker, status_code,
):
    def raise_err(*a, **kw):
        raise ClientError(status_code=status_code)

    client_mocker = async_client_mocker_factory()
    mocker.patch('connect.client.testing.models.mixins.ResourceMixin.get', side_effect=raise_err)

    with pytest.raises(ClientError):
        await ConnectAccountUser.retrieve('VA-123', 'UR-456', client_mocker)


@pytest.mark.asyncio
async def test_retrieve_ok(async_client_mocker_factory, mocker):
    user = UserFactory()

    client_mocker = async_client_mocker_factory()
    mocker.patch(
        'connect.client.testing.models.mixins.ResourceMixin.get',
        AsyncMock(return_value=user),
    )

    result = await ConnectAccountUser.retrieve('PA-123', user['id'], client_mocker)

    assert result == user
