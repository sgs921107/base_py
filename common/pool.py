#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: 协程池
'''
import time
import signal
import asyncio
import platform
from asyncio import Semaphore

from common import config


class SignalHandler(object):
    exit = False

    def add_signal_handler(self):
        if platform.system() == "Windows":
            for sig in [signal.SIGINT, signal.SIGTERM]:
                signal.signal(sig, self._close)
        else:
            for sig in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
                signal.signal(sig, self._close)

    def scan_iter(self, data):
        """
        将数据转换为生成器
        当收到退出信号时停止迭代
        """
        for item in data:
            if self.exit:
                break
            yield item

    @classmethod
    def sleep(cls, timeout):
        sleep_task = asyncio.ensure_future(asyncio.sleep(timeout))
        while not (cls.exit | sleep_task.done()):
            time.sleep(0.1)

    @classmethod
    async def asleep(cls, timeout):
        sleep_task = asyncio.ensure_future(asyncio.sleep(timeout))
        while not (cls.exit | sleep_task.done()):
            await asyncio.sleep(0.1)

    @staticmethod
    def _close(signum, frame):
        SignalHandler.exit = True

    @classmethod
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        # 添加信号处理
        obj.add_signal_handler()
        return obj


class AsyncPool(SignalHandler):

    def __init__(
        self,
        concurrent: int = config.mysql_pool_size,
    ):
        """
        concurrent: 并发数, 应不大于db连接池的最大数量
        """
        super().__init__()
        self._join = False
        self.tasks = set()
        self.sem = Semaphore(concurrent)

    def done_callback(self, task):
        """
        异步任务结束后, 从任务集合删除
        """
        self.tasks.remove(task)

    async def handler(self, coro_or_future):
        async with self.sem:
            await coro_or_future

    def sync(self, coro_or_future, callback=None):
        if self._join:
            raise("AsyncPool Joined")
        task = asyncio.ensure_future(self.handler(coro_or_future))
        if callback is not None:
            task.add_done_callback(callback)
        self.tasks.add(task)
        task.add_done_callback(self.done_callback)
        return task

    def map(self, func, iterable, callback=None):
        tasks = list()
        return [self.sync(func(param), callback=callback) for param in iterable]

    async def wait(self):
        # 等待所有数据存储完毕
        if self.tasks:
            await asyncio.wait(self.tasks)

    async def join(self):
        self._join = True
        await self.wait()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, exc_trace):
        await self.join()

