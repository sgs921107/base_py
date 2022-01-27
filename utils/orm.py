#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: orm
'''

from logging import DEBUG

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from common import config, logger


class DB(object):
    instance = None
    sync_instance = None
    session = None
    sync_session = None

    @classmethod
    def get_session(cls, sync=True):
        session_attr = (sync and "sync_" or "") + "session"
        session = getattr(cls, session_attr)
        if session is None:
            session_cls = sync and AsyncSession or Session
            session = sessionmaker(
                cls.get_instance(sync),
                class_=session_cls,
            )
            setattr(
                cls,
                session_attr,
                session
            )
        return session()

    @staticmethod
    def create_url(sync=True):
        """
        生成连接db的url
        """
        return "mysql+%(driver)s://%(username)s:%(password)s@%(host)s:%(port)s/%(db)s?charset=%(charset)s" % {
            "driver": "aiomysql" if sync else "pymysql",
            "username": config.mysql_user,
            "password": config.mysql_password,
            "host": config.mysql_host,
            "port": config.mysql_port,
            "db": config.mysql_db,
            "charset": config.mysql_charset
        }

    @classmethod
    def get_instance(cls, sync=True):
        """
        获取一个db实例
        """
        attr = (sync and "sync_" or "") + "instance"
        instance = getattr(cls, attr)
        if instance is None:
            engine = create_engine(
                url=cls.create_url(sync),
                future=True,
                pool_size=config.mysql_pool_size,
                pool_recycle=-1,
                echo=logger.level == DEBUG,
                isolation_level="AUTOCOMMIT"
            )
            instance = sync and AsyncEngine(engine) or engine
            setattr(cls, attr, instance)
        return instance
