#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: 异步分页器
'''
from math import ceil
from sqlalchemy import func

from utils.orm import DB
from common.conts import DEFAULT_PAGE_SIZE


class AsyncPaginator(object):
    """
    异步分页器
    """

    def __init__(self, stmt, page: int = 1, size: int = DEFAULT_PAGE_SIZE):
        # 查询对象
        self.stmt = stmt
        self.page = page
        self.size = size

    async def total(self):
        """
        总计
        """
        async with DB.get_session() as session:
            result = await session.execute(
                self.stmt.with_only_columns(func.count("*"))
            )
            return result.scalar()

    async def pages(self):
        """
        总页数
        """
        return ceil(await self.total() / self.size)

    async def next_page(self):
        """
        下一页的页码
        """
        if self.page >= await self.pages():
            return None
        return self.page + 1

    async def has_next(self):
        """
        是否有下一页
        """
        return await self.next_page() is not None

    async def next_paginate(self):
        """
        下一页的分页器对象
        """
        next_page = await self.next_page()
        if next_page is None:
            return None
        return self.__class__(self.stmt, next_page, self.size)

    async def pre_page(self):
        """
        上一页的页码
        """
        if self.page <= 1:
            return None
        return self.page - 1

    async def has_pre(self):
        """
        是否有上一页
        """
        return await self.pre_page() is not None

    async def pre_paginate(self):
        """
        上一页的分页器对象
        """
        pre_page = await self.pre_page()
        if pre_page is None:
            return None
        return self.__class__(self.stmt, pre_page, self.size)

    async def items(self):
        async with DB.get_session() as session:
            return await session.execute(
                self.stmt.limit(
                    self.size
                ).offset(
                    self.size * (self.page - 1)
                )
            )
