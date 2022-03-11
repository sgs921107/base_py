#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 12:20:33
LastEditors: xiangcai
LastEditTime: 2022-03-10 12:25:34
Description: file content
'''

from fastapi import APIRouter

from web.api.v1.book.views import router as book_router


router = APIRouter()

router.include_router(book_router, prefix="/book")


if __name__ == '__main__':
    pass
