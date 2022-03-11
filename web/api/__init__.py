#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 12:25:23
LastEditors: xiangcai
LastEditTime: 2022-03-11 14:23:41
Description: file content
'''
from fastapi import APIRouter

from web.api.v1 import router as v1_router

router = APIRouter()

router.include_router(v1_router, prefix="/v1")

if __name__ == '__main__':
    pass
