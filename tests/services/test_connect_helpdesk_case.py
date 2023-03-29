# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from unittest.mock import AsyncMock

import pytest
from connect.client import ClientError

from dbaas.constants import DBAction, DBWorkload
from dbaas.services import ConnectHelpdeskCase

from tests.factories import CaseFactory, DBFactory


@pytest.mark.asyncio
async def test_create_from_db_document_client_error(mocker):
    def raise_err(*a, **kw):
        raise ClientError(status_code=503)

    db_document = DBFactory(
        id='PGDB-100',
        name='Richard Watts',
        description='lost',
        workload=DBWorkload.MEDIUM,
        tech_contact__id='UR-456',
        region__id='eu-west',
    )
    create_p = mocker.patch('dbaas.services.ConnectHelpdeskCase.create', side_effect=raise_err)
    inst_p = mocker.patch(
        'dbaas.services.ConnectInstallation.get_extension_owner_id', return_value='VA-123',
    )

    with pytest.raises(ClientError):
        await ConnectHelpdeskCase.create_from_db_document(
            db_document,
            action=DBAction.UPDATE,
            description='Some desc',
            installation='installation',
            client='client',
        )

    data = {
        'subject': 'Infra PGDB-100 update Richard Watts',
        'description': '\nID: PGDB-100\n'
                       'Name: Richard Watts\n'
                       'Action: update\n'
                       'Workload: medium\n'
                       'Region: eu-west\n'
                       'Contact: UR-456\n\n'
                       'Some desc\n',
        'priority': 2,
        'type': 'technical',
        'issuer': {
            'recipients': [{'id': 'UR-456'}],
        },
        'receiver': {
            'account': {'id': 'VA-123'},
        },
    }
    create_p.assert_called_once_with(data, 'client')
    inst_p.assert_called_once_with('installation')


@pytest.mark.asyncio
@pytest.mark.parametrize('action', (DBAction.UPDATE, DBAction.DELETE))
async def test_create_from_db_document_ok(mocker, action):
    db_document = DBFactory(
        id='DB-123',
        name='abc',
        description='lost',
        workload=DBWorkload.SMALL,
        tech_contact__id='UR-123',
        region__id='us-central',
    )
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
        action=action,
        description='-',
        installation='installation',
        client='client',
    )

    assert result == case

    data = {
        'subject': f'Infra DB-123 {action} abc',
        'description': '\nID: DB-123\n'
                       'Name: abc\n'
                       f'Action: {action}\n'
                       'Workload: small\n'
                       'Region: us-central\n'
                       'Contact: UR-123\n\n'
                       '-\n',
        'priority': 2,
        'type': 'technical',
        'issuer': {
            'recipients': [{'id': 'UR-123'}],
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
    async_client_mocker, status_code, async_connect_client,
):
    async_client_mocker('helpdesk').cases.create(status_code=status_code)

    with pytest.raises(ClientError):
        await ConnectHelpdeskCase.create({}, async_connect_client)


@pytest.mark.asyncio
async def test_create_ok(async_client_mocker, async_connect_client):
    helpdesk_case = CaseFactory()
    data = {'subject': 'some'}

    async_client_mocker('helpdesk').cases.create(return_value=helpdesk_case)

    result = await ConnectHelpdeskCase.create(data, async_connect_client)

    assert result == helpdesk_case
