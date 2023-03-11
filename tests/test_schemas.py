# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest
from fastapi.encoders import jsonable_encoder

from dbaas.constants import DBStatus, DBWorkload
from dbaas.schemas import DatabaseIn, DatabaseOutDetail, DatabaseOutList, RegionOut

from tests.factories import CaseFactory, DBFactory, RegionFactory


@pytest.mark.parametrize('data', [
    {
        'name': 'DB1',
        'description': 'Some desc',
        'workload': 'small',
        'tech_contact': {'id': 'UR-123-456'},
        'region': {'id': 'eu-west'},
    },
    {
        'name': 'x' * 128,
        'description': 'y' * 512,
        'workload': 'large',
        'tech_contact': {'id': 'U' * 32, 'name': 'user'},
        'region': {'id': 'us-central'},
    },
])
def test_database_in_ok(data):
    assert DatabaseIn(**data)


@pytest.mark.parametrize('data', [
    {},
    {
        'name': 'name',
        'description': 'desc',
        'workload': 'small',
    },
    {
        'name': None,
        'description': None,
        'workload': None,
        'tech_contact': {'id': None},
        'region': {'id': None},
    },
    {
        'name': 'name',
        'description': 'desc',
        'workload': 'random',
        'tech_contact': {'id': 'UR-123-456'},
        'region': {'id': 'region'},
    },
    {
        'name': None,
        'description': 'desc',
        'workload': 'medium',
        'tech_contact': {'id': 'UR-123-456'},
        'region': {'id': 'region'},
    },
    {
        'name': 'name',
        'description': 'd' * 1024,
        'workload': 'large',
        'tech_contact': {'id': 'UR-123-456'},
        'region': {'id': 'region'},
    },
])
def test_database_in_fail(data):
    with pytest.raises(ValueError):
        DatabaseIn(**data)


def test_database_out_list():
    db = DBFactory(
        id='DB-123',
        name='abc',
        description='xyz',
        workload=DBWorkload.LARGE,
        status=DBStatus.REVIEWING,
        region__id='eu',
        region__name='spain',
        tech_contact__id='UR-123',
        tech_contact__name='user',
        cases=CaseFactory.create_batch(2),
        events={'happened': {'at': 1}},
    )

    assert jsonable_encoder(DatabaseOutList(**db)) == {
        'name': 'abc',
        'description': 'xyz',
        'workload': 'large',
        'tech_contact': {'id': 'UR-123', 'name': 'user'},
        'region': {'id': 'eu', 'name': 'spain'},
        'id': 'DB-123',
        'status': 'reviewing',
        'case': None,
        'events': {'happened': {'at': 1}},
    }


def test_database_out_detail():
    db = DBFactory(
        id='DB-456',
        name='other',
        description='some long',
        workload=DBWorkload.MEDIUM,
        status=DBStatus.ACTIVE,
        region__id='us',
        region__name='texas',
        tech_contact__id='UR-456-789',
        tech_contact__name='abc',
        tech_contact__email='user@user.com',
        events={'passed': {'by': 2}},
        credentials={'password': 'qwerty'},
    )

    assert jsonable_encoder(DatabaseOutDetail(case=CaseFactory(id='CS-100'), **db)) == {
        'name': 'other',
        'description': 'some long',
        'workload': 'medium',
        'tech_contact': {'id': 'UR-456-789', 'name': 'abc', 'email': 'user@user.com'},
        'region': {'id': 'us', 'name': 'texas'},
        'id': 'DB-456',
        'status': 'active',
        'case': {'id': 'CS-100'},
        'events': {'passed': {'by': 2}},
        'credentials': {'password': 'qwerty'},
    }


def test_region_out():
    region_doc = RegionFactory(id='t', name='test')

    assert jsonable_encoder(RegionOut(**region_doc)) == {'id': 't', 'name': 'test'}
