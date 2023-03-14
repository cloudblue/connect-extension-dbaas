# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

import pytest

from dbaas.database import Collections
from dbaas.services import Region

from tests.factories import RegionFactory


@pytest.mark.asyncio
async def test_list_is_empty(db):
    results = await Region.list(db)

    assert results == []


@pytest.mark.asyncio
async def test_list_several_regions(db):
    r1 = RegionFactory(name='Europe')
    r2 = RegionFactory(name='Asia')
    db[Collections.REGION].insert_many([r1, r2])

    results = await Region.list(db)

    assert len(results) == 2
    assert [r['id'] for r in results] == [r['id'] for r in (r2, r1)]


@pytest.mark.asyncio
async def test_retrieve_is_found(db):
    db[Collections.REGION].insert_one(RegionFactory(id='test'))

    result = await Region.retrieve('test', db)

    assert result['id'] == 'test'


@pytest.mark.asyncio
async def test_retrieve_not_found(db):
    result = await Region.retrieve('abc', db)

    assert result is None
