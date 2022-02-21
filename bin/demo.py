#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: demo
'''
if __name__ == '__main__':
    # import __init__
    from importlib import import_module
    import_module("__init__")
from common import logger
from common.pool import SignalHandler


async def main():
    handler = SignalHandler()
    while handler.exit is False:
        logger.info("this is a demo")
        await handler.asleep(1)


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
