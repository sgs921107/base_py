#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 17:41:53
LastEditors: xiangcai
LastEditTime: 2022-03-11 10:40:21
Description: file content
'''
from fastapi import WebSocket, status

from common import logger


class WebsocketManager:
    """
    websocket连接管理
    """

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def connect(self):
        await self.websocket.accept()

    async def disconnect(self):
        await self.websocket.close(code=status.WS_1000_NORMAL_CLOSURE)

    async def send_message(self, message: str = ""):
        await self.websocket.send_text(message)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_trace):
        if exc_type:
            logger.error("%s: %s\r\n%s" % (exc_type, exc_value, exc_trace))
        await self.disconnect()


if __name__ == '__main__':
    pass
