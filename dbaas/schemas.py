# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Ingram Micro
# All rights reserved.
#

from typing import Literal, Optional

from pydantic import BaseModel, constr, Field

from dbaas.constants import DBWorkload


class JsonError(BaseModel):
    message: str


class RefIn(BaseModel):
    id: constr(min_length=1, max_length=32, strict=True)


BaseRefOut = RefIn


class RefOut(BaseRefOut):
    name: Optional[str] = None


class TechContactOut(RefOut):
    email: str


class DatabaseInUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    tech_contact: Optional[RefIn] = None


class DatabaseInCreate(DatabaseInUpdate):
    name: constr(min_length=1, max_length=128, strict=True)
    description: constr(min_length=1, max_length=512, strict=True)
    workload: Literal[DBWorkload.all()]
    tech_contact: RefIn
    region: RefIn


class DatabaseOutList(DatabaseInCreate):
    id: str
    region: RefOut
    tech_contact: RefOut
    status: str
    case: Optional[RefIn] = None
    events: Optional[dict] = None


class DatabaseOutDetail(DatabaseOutList):
    tech_contact: TechContactOut
    credentials: Optional[dict] = None


class _DatabaseReconfigureCase(BaseModel):
    subject: constr(min_length=1, max_length=300, strict=True)
    description: Optional[str] = Field('DB reconfiguration.', max_length=1000)


class DatabaseReconfigure(BaseModel):
    case: _DatabaseReconfigureCase


RegionOut = RefOut
