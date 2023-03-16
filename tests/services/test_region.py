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
    await db[Collections.REGION].insert_many([r1, r2])

    results = await Region.list(db)

    assert len(results) == 2
    assert [r['id'] for r in results] == [r['id'] for r in (r2, r1)]


@pytest.mark.asyncio
async def test_retrieve_is_found(db):
    await db[Collections.REGION].insert_one(RegionFactory(id='test'))

    result = await Region.retrieve('test', db)

    assert result['id'] == 'test'


@pytest.mark.asyncio
async def test_retrieve_not_found(db):
    result = await Region.retrieve('abc', db)

    assert result is None


@pytest.mark.asyncio
async def test_create_ok(db):
    data = RegionFactory()

    result = await Region.create(data, db)
    region_document_from_db = await db[Collections.REGION].find_one({'id': data['id']})

    assert result == data
    assert region_document_from_db['id'] == data['id']
    assert region_document_from_db['name'] == data['name']

    count_docs = await db[Collections.REGION].count_documents({})
    assert count_docs == 1


@pytest.mark.asyncio
async def test_create_duplicate_id(db):
    data = RegionFactory()
    await Region.create(data, db)

    with pytest.raises(ValueError) as e:
        await Region.create(data, db)

    assert str(e.value) == 'ID must be unique.'

    count_docs = await db[Collections.REGION].count_documents({})
    assert count_docs == 1
