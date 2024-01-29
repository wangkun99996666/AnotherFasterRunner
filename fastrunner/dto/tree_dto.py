# !/usr/bin/python3
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field


class TreeUniqueIn(BaseModel):
    project_id: int
    type: int


class TreeUpdateIn(BaseModel):
    tree: list[dict] = Field(alias='body')


class TreeOut(BaseModel):
    tree: list[dict]
    id: int
    max: int
