#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 15:56:04
LastEditors: xiangcai
LastEditTime: 2022-03-11 10:06:29
Description: file content
'''
from typing import Optional, Any

from fastapi import Query


def gen_constraint(
    *,
    alias: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    regex: Optional[str] = None,
    deprecated: Optional[bool] = None,
    example: Any = None,
    **extra: Any,
):
    """
    生成字段约束
    """
    options = extra.copy()
    options.update({
        "alias": alias,
        "title": title,
        "description": description,
        "gt": gt,
        "ge": ge,
        "lt": lt,
        "le": le,
        "min_length": min_length,
        "max_length": max_length,
        "regex": regex,
        "deprecated": deprecated,
        "example": example
    })
    return options


page_constraint = gen_constraint(ge=1, description="page num", example=1)
page_size_constraint = gen_constraint(ge=10, le=50, description="page size", example=10)


def validate_page(page: int = Query(1, **page_constraint)):
    return page


def validate_size(size: int = Query(10, **page_size_constraint)):
    return size


if __name__ == '__main__':
    pass
