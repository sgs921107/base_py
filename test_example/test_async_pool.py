#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: file content
'''
import time
import asyncio
from math import ceil

import pytest

from common.pool import AsyncPool


class TestAsyncPool(object):
    sleep_second = 0.5
    pool_size = 5
    work_times = 10

    @pytest.mark.asyncio
    async def test_sync(self):
        st = time.time()
        pool = AsyncPool(self.pool_size)
        for i in pool.scan_iter(range(self.work_times)):
            pool.sync(self.work(i), callback=self.callback)
        await pool.join()
        task_time = time.time() - st
        want = ceil(self.work_times / self.pool_size) * self.sleep_second
        assert task_time >= want, "want task_time >= %d, have %s" % (want, task_time)

    @pytest.mark.asyncio
    async def test_map(self):
        st = time.time()
        pool = AsyncPool(self.pool_size)
        pool.map(self.work, range(self.work_times, self.work_times * 2), callback=self.callback)
        await pool.join()
        task_time = time.time() - st
        want = ceil(self.work_times / self.pool_size) * self.sleep_second
        assert task_time >= want, "want task_time >= %d, have %s" % (want, task_time)

    @pytest.mark.asyncio
    async def test_context(self):
        p = None
        async with AsyncPool(self.pool_size) as pool:
            pool.sync(self.work(100))
            p = pool
        assert p._join is True, "want p._join is True, have %s" % p._join

    @staticmethod
    def callback(task):
        pass

    async def work(self, num):
        await asyncio.sleep(self.sleep_second)


if __name__ == '__main__':
    pass
