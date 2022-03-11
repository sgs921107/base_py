#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 10:03:25
LastEditors: xiangcai
LastEditTime: 2022-03-10 18:03:45
Description: file content
'''
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from common import config
from common.conts import DEVELOP
from web.api import router as api_router

default_succeed_schema = {
    "code": "int",
    "msg": "string",
    "data": "any"
}

app = FastAPI(
    debug=config.srv_environment == DEVELOP,
    docs_url=config.srv_environment == DEVELOP and "/docs" or None,
    redocs_url=config.srv_environment == DEVELOP and "/redoc" or None,
    version="0.1.0",
    title="FastAPI",
    description="This is a demo"
)

# 允许跨域
allow_origins = [
    '*',
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

allowed_hosts = [
    "*",
]

# 允许访问hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 挂载静态服务器
cur_dir = os.path.dirname(os.path.realpath(__file__))
static_path = os.path.join(cur_dir, "static")
app.mount("/static", StaticFiles(directory=static_path, check_dir=True))


@app.get("/")
async def index():
    return RedirectResponse("/static/html/index.html")


app.include_router(api_router, prefix="/api")

if __name__ == '__main__':
    pass
