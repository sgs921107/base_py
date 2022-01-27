#!/usr/bin/env python
# -*- coding=utf8 -*-

import time
import socket
import platform
from datetime import timedelta

# 日期格式
LAYOUT_ISO = "%Y-%m-%d %H:%M"
LAYOUT_ISO_SIMPLE = "%Y-%m-%d %H:%M:%S"
LAYOUT_UTC = "%d.%m.%Y %H:%M"
LAYOUT_DATE_UTC = "%d.%m.%Y"
LAYOUT_DATE_ISO = "%Y-%m-%d"
LAYOUT_DATE_CST = "%Y%m%d"
LAYOUT_DATE_ATG = "%d-%m-%Y"

# 时间单位(非常量)
DAY = timedelta(days=1)
HOUR = timedelta(hours=1)
MINUTE = timedelta(minutes=1)
SECOND = timedelta(seconds=1)

# 时区
# 东八时区
CCT = 8
# 当前服务器的时区
CUR_TIMEZONE = time.timezone // 60 // 60 * -1
# 默认时区(当前时区)
DEFAULT_TIMEZONE = None

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB

DEVELOP = "develop"
ON = 1
OFF = 0

# 默认gzip zlib加密等级
DEFAULT_COMPRESS_LEVEL = 9

# 编码
LATIN1 = "latin-1"
UTF8 = "utf-8"

# env配置文件的路径
ENV_PATH = "/projects/.env"

# 日志
DEFAULT_LOG_FORMAT = "%(asctime)s - pid:%(process)d - %(filename)s [line: %(lineno)d] [%(levelname)s] ----- %(message)s"
DEFAULT_LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


# socket保活选项
DEFAULT_SOCKET_KEEPALIVE_OPTIONS = {
    socket.TCP_KEEPINTVL: 10,
    socket.TCP_KEEPCNT: 3
}
if platform.system() != "Darwin":
    # mac不支持此参数
    DEFAULT_SOCKET_KEEPALIVE_OPTIONS[socket.TCP_KEEPIDLE] = 30

# 分页器的默认page size
DEFAULT_PAGE_SIZE = 100
# 默认的redis key过期时间 单位: 秒
DEFAULT_REDIS_EXPIRES = int(DAY.total_seconds())
# 默认的队列长度 有序集合,列表
DEFAULT_REDIS_QUEUE_SIZE = 10000
# 默认redis配置
DEFAULT_REDIS_PARAMS = {
    "encoding": "utf-8",
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'socket_keepalive': True,
    'socket_keepalive_options': DEFAULT_SOCKET_KEEPALIVE_OPTIONS,
    'retry_on_timeout': True,
    'max_connections': 0,
    'decode_responses': True
}


DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
}
