# -*- coding: utf-8 -*-
#
# Copyright (c) 2025, CloudBlue
# All rights reserved.
#

from typing import Literal, Optional

from pydantic import BaseModel, constr, Field

from dbaas.constants import DBAction, DBWorkload


class JsonError(BaseModel):
    message: str


class RefIn(BaseModel):
    id: constr(min_length=1, max_length=32, strict=True)


BaseRefOut = RefIn


class RefOut(BaseRefOut):
    name: Optional[str]


class TechContactOut(RefOut):
    email: str


class DatabaseInUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    description: Optional[str] = Field(None, max_length=512)
    tech_contact: Optional[RefIn]


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
    owner: RefIn
    case: Optional[RefIn]
    events: Optional[dict]


class _Credentials(BaseModel):
    host: str
    username: str
    password: str
    name: Optional[str]


class DatabaseOutDetail(DatabaseOutList):
    tech_contact: TechContactOut
    credentials: Optional[_Credentials]


class DatabaseReconfigure(BaseModel):
    action: Literal[DBAction.DELETE, DBAction.UPDATE]
    details: Optional[str] = Field(None, max_length=700)


class DatabaseActivate(BaseModel):
    workload: Optional[Literal[DBWorkload.all()]]
    credentials: Optional[_Credentials]


RegionOut = RefOut


class RegionIn(RefIn):
    name: constr(min_length=1, max_length=64, strict=True)
