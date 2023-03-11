# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from typing import Literal, Optional

from pydantic import BaseModel, Field

from dbaas.constants import DBWorkload


class JsonError(BaseModel):
    message: str


class RefIn(BaseModel):
    id: str = Field(..., max_length=32)


BaseRefOut = RefIn


class RefOut(BaseRefOut):
    name: Optional[str] = None


class TechContactOut(RefOut):
    email: str


class DatabaseIn(BaseModel):
    name: str = Field(..., max_length=128)
    description: str = Field(..., max_length=512)
    workload: Literal[DBWorkload.all()]
    tech_contact: RefIn
    region: RefIn


class DatabaseOutList(DatabaseIn):
    id: str
    region: RefOut
    tech_contact: RefOut
    status: str
    case: Optional[RefIn] = None
    events: Optional[dict] = None


class DatabaseOutDetail(DatabaseOutList):
    tech_contact: TechContactOut
    credentials: Optional[dict] = None


RegionOut = RefOut
