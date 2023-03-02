# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest

from dbaas.schemas import DatabaseIn


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
