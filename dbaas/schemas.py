# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from typing import Literal, Optional

from pydantic import BaseModel, Field

from dbaas.constants import DBWorkload


class Ref(BaseModel):
    id: str = Field(..., max_length=32)


class InnerRefOut(Ref):
    name: Optional[str] = None


class DatabaseIn(BaseModel):
    name: str = Field(..., max_length=128)
    description: str = Field(..., max_length=512)
    workload: Literal[DBWorkload.all()]
    tech_contact: Ref
    region: Ref


class DatabaseOutList(DatabaseIn):
    id: str
    region: InnerRefOut
    status: str
    case: Optional[Ref] = None
    events: Optional[dict] = None


class DatabaseOutDetail(DatabaseOutList):
    credentials: Optional[dict] = None


RegionOut = InnerRefOut
