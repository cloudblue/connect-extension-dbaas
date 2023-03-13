# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from unittest.mock import AsyncMock

import pytest
from connect.client import ClientError

from dbaas.services import ConnectHelpdeskCase

from tests.factories import CaseFactory, DBFactory


@pytest.mark.asyncio
async def test_create_from_db_document_client_error(mocker):
    def raise_err(*a, **kw):
        raise ClientError(status_code=503)

    db_document = DBFactory(id='PGDB-100', tech_contact__id='UR-456')
    create_p = mocker.patch('dbaas.services.ConnectHelpdeskCase.create', side_effect=raise_err)
    inst_p = mocker.patch(
        'dbaas.services.ConnectInstallation.get_extension_owner_id', return_value='VA-123',
    )

    with pytest.raises(ClientError):
        await ConnectHelpdeskCase.create_from_db_document(
            db_document,
            subject='Request to create PGDB-100.',
            description='Some desc',
            installation='installation',
            client='client',
        )

    data = {
        'subject': 'Request to create PGDB-100.',
        'description': 'Some desc',
        'priority': 2,
        'type': 'business',
        'issuer': {
            'recipients': [
                {'id': 'UR-456'},
            ],
        },
        'receiver': {
            'account': {'id': 'VA-123'},
        },
    }
    create_p.assert_called_once_with(data, 'client')
    inst_p.assert_called_once_with('installation')


@pytest.mark.asyncio
async def test_create_from_db_document_ok(mocker):
    db_document = DBFactory(id='DB-123', tech_contact__id='UR-123')
    case = CaseFactory()
    create_p = mocker.patch(
        'dbaas.services.ConnectHelpdeskCase.create',
        AsyncMock(return_value=case),
    )
    inst_p = mocker.patch(
        'dbaas.services.ConnectInstallation.get_extension_owner_id', return_value='PA-123',
    )

    result = await ConnectHelpdeskCase.create_from_db_document(
        db_document,
        subject='Request to create DB-123.',
        description='desc test',
        installation='installation',
        client='client',
    )

    assert result == case

    data = {
        'subject': 'Request to create DB-123.',
        'description': 'desc test',
        'priority': 2,
        'type': 'business',
        'issuer': {
            'recipients': [
                {'id': 'UR-123'},
            ],
        },
        'receiver': {
            'account': {'id': 'PA-123'},
        },
    }
    create_p.assert_called_once_with(data, 'client')
    inst_p.assert_called_once_with('installation')


@pytest.mark.asyncio
@pytest.mark.parametrize('status_code', (400, 503))
async def test_create_bad_response_from_connect_api(
    async_client_mocker_factory, mocker, status_code,
):
    def raise_err(*a, **kw):
        raise ClientError(status_code=status_code)

    client_mocker = async_client_mocker_factory()
    p = mocker.patch(
        'connect.client.testing.models.base.CollectionMock.create',
        side_effect=raise_err,
    )

    with pytest.raises(ClientError):
        await ConnectHelpdeskCase.create({}, client_mocker)

    p.assert_called_once_with(payload={})


@pytest.mark.asyncio
async def test_create_ok(async_client_mocker_factory, mocker):
    helpdesk_case = CaseFactory()
    data = {'subject': 'some'}

    client_mocker = async_client_mocker_factory()
    p = mocker.patch(
        'connect.client.testing.models.base.CollectionMock.create',
        AsyncMock(return_value=helpdesk_case),
    )

    result = await ConnectHelpdeskCase.create(data, client_mocker)

    assert result == helpdesk_case

    p.assert_called_once_with(payload=data)
