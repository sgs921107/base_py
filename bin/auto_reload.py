#!/usr/bin/env python
# -*- coding=utf8 -*-
if __name__ == '__main__':
    # 执行脚本前将项目目录添加至path
    from importlib import import_module
    import_module('.', '__init__')
import asyncio
import subprocess

from inotify.adapters import Inotify # type: ignore

from common import logger
from common.conts import ENV_PATH
from common.pool import SignalHandler


class AutoReload(SignalHandler):

    def __init__(self, env_path=ENV_PATH, nones=10, interval=60):
        # 监听配置文件
        self.inotify = Inotify(paths=[env_path])
        # 是否应该重启
        self.should_reload = False
        # 用来控制间当有文件修改后隔多少秒没有写关闭事件后执行reload
        self.nones = nones
        # 间隔多少秒可以执行一次reload
        self.interval = interval

    async def reload(self):
        while self.exit is False:
            if self.should_reload is False:
                logger.debug("don't need reload")
                await self.asleep(1)
                continue
            else:
                logger.info('start reload circus')
                # 启动子进程执行reload操作
                reload_code, output = subprocess.getstatusoutput('circusctl reload')
                if reload_code == 0:
                    logger.info("execute reload circus succeed: %s" % output)
                    self.should_reload = False
                else:
                    logger.error("reload circus failed: %s" % output)
                    if 'Timed out' in output:
                        logger.error("请检查circusd是否启动")
                    elif "already running arbiter_reload" in output:
                        logger.error("正在reload中,请不要频繁执行reload命令")
                await self.asleep(self.interval)
                logger.info('circus reload done')

    async def handler_inotify(self):
        nones = 0
        should_reload = False
        for event in self.scan_iter(self.inotify.event_gen(yield_nones=True)):
            if event is None:
                if should_reload:
                    nones += 1
                if nones >= self.nones:
                    self.should_reload = True
                    should_reload = False
                await self.asleep(0.01)
            else:
                nones = 0
                if 'IN_CLOSE_WRITE' in event[1]:
                    logger.info('file modified: %s' % event[-2])
                    should_reload = True

    async def run(self):
        await asyncio.gather(
            asyncio.ensure_future(self.reload()),
            asyncio.ensure_future(self.handler_inotify())
        )


if __name__ == '__main__':
    ar = AutoReload()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ar.run())
