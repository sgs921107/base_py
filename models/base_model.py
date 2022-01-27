#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2021-09-06 17:38:27
LastEditors: xiangcai
LastEditTime: 2022-01-27 11:10:37
Description: file content
'''
import json
from datetime import datetime
from functools import partial
from typing import Iterable, Dict

from sqlalchemy.util import immutabledict
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, text, insert, select, update
from sqlalchemy.dialects.mysql import INTEGER, TIMESTAMP, \
    VARCHAR, TEXT, CHAR

from utils.orm import DB
from utils.async_redis import ARedis
from utils.paginate import AsyncPaginator
from common import config, logger
from common.funcs import now_datetime, updated_data
from common.conts import LAYOUT_ISO_SIMPLE, DEFAULT_REDIS_EXPIRES

# 字符排序规则
CHAR_COLLATE = "utf8mb4_unicode_ci"
# 对string类型指定排序集
UNICODE_TEXT = partial(TEXT, collation=CHAR_COLLATE)
UNICODE_CHAR = partial(CHAR, collation=CHAR_COLLATE)
UNICODE_VARCHAR = partial(VARCHAR, collation=CHAR_COLLATE)

Base = declarative_base()
# 修改默认索引名的规则, 方便修改自动生成的迁移文件
Base.metadata.naming_convention = immutabledict({"ix": "ix_%(column_0_name)s"})

redis_cli = ARedis.get_instance()


def real_table(name: str) -> str:
    """
    格式化表名
    """
    if config.mysql_prefix.endswith("_"):
        return config.mysql_prefix + name
    return "_".join([config.mysql_prefix, name])


class BaseModel(Base):
    __abstract__ = True
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    id = Column(
        "id", INTEGER(11, unsigned=True), primary_key=True, comment="自增id"
    )
    created_at = Column(
        "created_at",
        TIMESTAMP(14),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="生成时间"
    )
    updated_at = Column(
        "updated_at",
        TIMESTAMP(14),
        nullable=False,
        # onupdate=datetime.now,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间"
    )
    deleted_at = Column(
        "deleted_at",
        TIMESTAMP(14),
        nullable=True,
        server_default=text("null"),
        comment="删除时间"
    )

    @classmethod
    def output_columns(cls):
        """
        移除生成时间、更新时间、删除时间
        """
        attr = "_output_columns"
        if not hasattr(cls, attr):
            columns = cls.__table__.columns
            output = list(columns)
            output.remove(columns.created_at)
            output.remove(columns.updated_at)
            output.remove(columns.deleted_at)
            setattr(cls, attr, output)
        return getattr(cls, attr)

    @classmethod
    def row_to_dict(cls, row):
        """
        将查询结果转化为字典
        """
        if row is None:
            return dict()
        data = dict()
        for key, value in zip(row.keys(), row):
            if isinstance(value, datetime):
                value = value.strftime(LAYOUT_ISO_SIMPLE)
            data[key] = value
        return data

    @classmethod
    def rows_to_dict(cls, rows):
        """
        将所有查询结果转化为字典
        """
        return [cls.row_to_dict(row) for row in rows]

    def dict(self):
        """
        将模型转化为字典
        """
        data = dict()
        for column in self.__table__.columns:
            name = column.name
            value = getattr(self, name)
            if value is None:
                continue
            elif isinstance(value, datetime):
                value = value.strftime(LAYOUT_ISO_SIMPLE)
            data[name] = value
        return data

    async def select_by_id(self):
        """
        根据id查询数据
        """
        if not self.id:
            logger.error("data id not found: %s" % self.dict())
            return dict()
        # 缓存中没有则从db查询
        async with DB.get_session() as session:
            result = await session.execute(
                select(self.output_columns()).where(
                    self.__class__.id == self.id
                ).limit(1)
            )
            return self.row_to_dict(result.first())

    async def update_by_id(self, data):
        """
        根据id更新数据
        return 影响的行数
        """
        if not self.id:
            logger.error("data id not found: %s" % self.dict())
            return 0
        async with DB.get_session() as session:
            async with session.begin():
                result = await session.execute(
                    update(self.__table__).values(data).where(
                        self.__class__.id == self.id
                        # False - 不对session进行同步，直接进行delete or update操作。
                    ).execution_options(synchronize_session=False))
                return result.rowcount

    async def insert(self):
        """
        将数据插入db
        return: 插入后的id/0
        """
        async with DB.get_session() as session:
            async with session.begin():
                result = await session.execute(
                    insert(
                        self.__table__
                    ).prefix_with(" ignore").values(**self.dict())
                )
                return result.lastrowid

    @classmethod
    async def select(
        cls,
        columns: Iterable,
        *conditions,
        distinct: bool = False,
        having=None,
        group_by=None,
        order_by=None,
        page=1,
        size=1000
    ):
        stmt = select(
            columns,
            whereclause=cls.deleted_at.is_(None),
            group_by=group_by,
            distinct=distinct,
            order_by=order_by,
            having=having,
        ).where(*conditions)
        return AsyncPaginator(stmt, page, size)

    @classmethod
    async def update(
        cls,
        values: Dict,
        *conditions: Iterable,
    ):
        async with DB.get_session() as session:
            stmt = update(
                cls.__table__,
                whereclause=cls.deleted_at.is_(None),
                values=values
            ).where(*conditions)
            result = await session.execute(
                # fetch 在delete or update操作之前，先发一条sql到数据库获取符合条件的记录
                stmt.execution_options(synchronize_session="fetch")
            )
            return result.rowcount

    @classmethod
    async def delete(
        cls,
        *conditions: Iterable,
    ):
        await cls.update(
            {cls.deleted_at.name: now_datetime()},
            *conditions
        )

    async def cache_data(self, search=False, expires=DEFAULT_REDIS_EXPIRES):
        if search:
            # 将db中的最新数据写入缓存
            data = await self.select_by_id()
        else:
            data = self.dict()
        ret = await redis_cli.hmsetex(self.cache_key, data, expires)
        logger.debug("save a %s item: %s" % (self.__class__.__name__, data))
        return ret

    async def save(self, use_cache=True, cache=True, expires=DEFAULT_REDIS_EXPIRES):
        """
        存储数据
        param use_cache: 获取原数据时是否从缓存中获取
        param cache: 存储数据到db后是否缓存至redis
        param expires: 缓存过期时间
        """
        # 尝试获取原数据
        ori_data = await self.ori_data(use_cache)
        data = self.dict()
        if ori_data:
            # 判断数据是否有变动
            updated = updated_data(data, ori_data)
            # 如果数据没有变更, 则不处理
            if not updated:
                return
            self.id = ori_data.get("id")
            rowcount = await self.update_by_id(updated)
            if cache:
                # 将db中的最新数据写入缓存
                await self.cache_data(rowcount == 0, expires)
            return rowcount > 0
        else:
            # 插入数据
            self.id = await self.insert()
            if cache and self.id:
                # 将db中的最新数据写入缓存
                await self.cache_data(False, expires)
            return self.id > 0

    async def ori_data(self, use_cache=False):
        if use_cache:
            # 首先尝试从缓存中获取
            cache = await redis_cli.hgetall(self.cache_key)
            if cache:
                return cache
        # 缓存中没有则从db查询
        async with DB.get_session() as session:
            result = await session.execute(
                select(self.output_columns()).where(
                    *self.ori_data_conditions()
                ).limit(1)
            )
            return self.row_to_dict(result.first())

    def ori_data_conditions(self):
        # example: return [self.__class__.id == self.id]
        raise AttributeError(
            "a %s subclass must hasattr ori_data_conditions"
            % self.__class__.__name__
        )

    @property
    def cache_key(self):
        raise AttributeError(
            "a %s subclass must hasattr cache_key"
            % self.__class__.__name__
        )

    def __repr__(self):
        data = {
            "model": self.__class__.__name__,
            "fields": self.dict()
        }
        return json.dumps(data, ensure_ascii=False, indent=4)
