#!/usr/bin/env python
# -*- coding=utf8 -*-
if __name__ == '__main__':
    # 执行脚本前将项目目录添加至path
    from importlib import import_module
    import_module('.', '__init__')
from web import app
from common.config import logging_config


if __name__ == '__main__':
    import uvicorn
    host = "0.0.0.0"
    port = 8000
    uvicorn.run(app, host=host, port=port, log_config=logging_config, loop="none")
