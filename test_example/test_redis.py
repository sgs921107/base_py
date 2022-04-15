#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-02-16 11:18:56
LastEditors: xiangcai
LastEditTime: 2022-04-15 17:04:02
Description: file content
'''
import pytest
import asyncio


class TestRedis(object):

    @pytest.mark.asyncio
    async def test_lpoptrim(self, redis_cli):
        name = "test_list_lpoptrim"
        num = 10
        await redis_cli.delete(name)
        # [0, 1, 2, ..., 19]
        await redis_cli.lpush(name, *list(range(num * 2))[::-1])
        # ["0", "1", "2", ..., "9"]
        lpop_want = [str(num) for num in range(num)]
        lpop_have = await redis_cli.lpoptrim(name, num)
        assert lpop_have == lpop_want, "lpop_want %s, have %s" % (lpop_want, lpop_have)
        # ["10", "11", "12", ..., "19"]
        remaining_want = [str(num) for num in range(num, num * 2)]
        remaining_have = await redis_cli.lrange(name, 0, -1)
        assert remaining_have == remaining_want, "remaining want %s, have %s" % (remaining_want, remaining_have)
        await redis_cli.delete(name)

    @pytest.mark.asyncio
    async def test_rpoptrim(self, redis_cli):
        name = "test_list_rpoptrim"
        num = 10
        await redis_cli.delete(name)
        # [19, 18, 17, ..., 0]
        await redis_cli.lpush(name, *list(range(num * 2)))
        # ["0", "1", "2", ..., "9"]
        lpop_want = [str(num) for num in range(num)]
        lpop_have = await redis_cli.rpoptrim(name, num)
        assert lpop_have == lpop_want, "lpop_want %s, have %s" % (lpop_want, lpop_have)
        # ["19", "18", "17", ..., "10"]
        remaining_want = [str(num - 1) for num in range(num * 2, num, -1)]
        remaining_have = await redis_cli.lrange(name, 0, -1)
        assert remaining_have == remaining_want, "remaining want %s, have %s" % (remaining_want, remaining_have)
        await redis_cli.delete(name)

    @pytest.mark.asyncio
    async def test_pubsub(self, redis_cli):
        channel = "test_channel"
        num = 5
        base_message = "this is a test: %d"
        # 订阅频道
        pubsub = await redis_cli.subscribe(channel)

        async def sub():
            """
            获取num条订阅消息
            """
            times = 0
            while times < num:
                message = await pubsub.get_message(timeout=1)
                if message is None or message.get("type") != redis_cli.MessageType.message:
                    continue
                message_data = message.get("data")
                want = base_message % times
                assert message_data == want, "want message_data == %s, have %s" % (want, message_data)
                times += 1
        sub_task = asyncio.ensure_future(sub())
        # 发布num条消息
        for i in range(num):
            message = base_message % i
            await redis_cli.publish(channel, message)
        await sub_task

    @pytest.mark.asyncio
    async def test_spoprem(self, redis_cli):
        # 测试的set name
        key = "test_set_sccan"
        await redis_cli.delete(key)
        size = 10
        # 测试数据
        data = {str(num) for num in range(size)}
        # 将测试数据添加至redis集合
        await redis_cli.saddex(key, *data)
        have_num = size // 2
        # 随机取出一半数据
        have_data = await redis_cli.spoprem(key, have_num)
        assert len(have_data) == have_num, "want len(have_data) == %s, have %d" % (have_num, len(have_data))
        remaining_num = size - have_num
        # redis中剩余的元素
        remaining_data = await redis_cli.smembers(key)
        assert len(remaining_data) == remaining_num, "want len(remaining_data) == %d, have %d" % (remaining_num, len(remaining_data))
        assert data == remaining_data | set(have_data), "want have_data | remaining_data == %s, have %s" % (data, have_data + remaining_data)
        await redis_cli.delete(key)

    @pytest.mark.asyncio
    async def test_lpushex(self, redis_cli):
        ex = 10
        name = "test_list_lpushex"
        await redis_cli.delete(name)
        data = [str(num) for num in range(10)]
        # 插入数据
        count = await redis_cli.lpushex(name, *data, ex=ex)
        assert count == len(data), "want count == %d, have %d" % (count, len(data))
        # 后去所有数据
        have = await redis_cli.lrange(name, 0, -1)
        want = data[::-1]
        assert have == want, "want %s, have %s" % (want, have)
        # 获取过期时间
        have_ex = await redis_cli.ttl(name)
        assert have_ex <= ex, "want have_ex <= %d, have %d" % (ex, have_ex)

    @pytest.mark.asyncio
    async def test_rpushex(self, redis_cli):
        ex = 10
        name = "test_list_rpushex"
        await redis_cli.delete(name)
        data = [str(num) for num in range(10)]
        # 插入数据
        count = await redis_cli.rpushex(name, *data, ex=ex)
        assert count == len(data), "want count == %d, have %d" % (count, len(data))
        # 后去所有数据
        have = await redis_cli.lrange(name, 0, -1)
        assert have == data, "want %s, have %s" % (data, have)
        # 获取过期时间
        have_ex = await redis_cli.ttl(name)
        assert have_ex <= ex, "want have_ex <= %d, have %d" % (ex, have_ex)


if __name__ == '__main__':
    pass
