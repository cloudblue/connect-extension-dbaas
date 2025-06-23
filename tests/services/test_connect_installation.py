# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, CloudBlue
# All rights reserved.
#

from unittest.mock import AsyncMock

import pytest
from connect.client import ClientError

from dbaas.services import ConnectInstallation

from tests.factories import InstallationFactory


@pytest.mark.asyncio
async def test_retrieve_client_error(mocker):
    def raise_err(*a, **kw):
        raise ClientError(status_code=503)

    p = mocker.patch('dbaas.services.get_installation', side_effect=raise_err)

    with pytest.raises(ClientError):
        await ConnectInstallation.retrieve('ENVI-1', 'client')

    p.assert_called_once_with('client', x_connect_installation_id='ENVI-1')


@pytest.mark.asyncio
async def test_retrieve_ok(async_client_mocker_factory, mocker):
    installation = InstallationFactory()
    p = mocker.patch('dbaas.services.get_installation', AsyncMock(return_value=installation))

    result = await ConnectInstallation.retrieve(installation['id'], 'client')

    assert result == installation

    p.assert_called_once_with('client', x_connect_installation_id=installation['id'])


def test_get_extension_owner_id_client_error():
    with pytest.raises(ClientError) as e:
        ConnectInstallation.get_extension_owner_id({})

    assert e.value.status_code == 500


def test_get_extension_owner_id_ok():
    installation = InstallationFactory(environment__extension__owner__id='VA-123-456')

    assert ConnectInstallation.get_extension_owner_id(installation) == 'VA-123-456'
