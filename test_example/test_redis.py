#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-02-16 11:18:56
LastEditors: xiangcai
LastEditTime: 2022-02-22 19:59:36
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


if __name__ == '__main__':
    pass
