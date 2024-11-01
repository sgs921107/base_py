#!/usr/bin/env python
# -*- coding=utf8 -*-

import asyncio
import pytest
from logging import INFO

from common import logger
from utils.orm import DB
from utils.async_redis import ARedis

if logger.level > INFO:
    logger.setLevel("INFO")


def pytest_addoption(parser):
    """
    添加自定义命令行参数
    """
    parser.addoption("--dev", "--develop", action="store_true", help="是否是开发环境")


@pytest.fixture(scope="session")
def redis_cli():
    cli = ARedis.get_instance()
    yield cli


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def db():
    instance = DB.get_instance()
    yield instance


# @pytest.fixture(scope="function")
# @pytest.mark.asyncio
# async def db_session():
#     session = DB.get_session()
#     yield session
#     await session.close()


@pytest.fixture(scope="session")
def is_develop(request):
    return request.config.getoption("--develop")
