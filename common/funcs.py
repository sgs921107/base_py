#!/usr/bin/env python
# -*- coding=utf8 -*-

import json
import time
from hashlib import md5, sha256, sha1
from datetime import datetime, timedelta
from zlib import compress as zcompress, decompress as zdecompress
from gzip import compress as gcompress, decompress as gdecompress

from common import logger
from common.conts import DEFAULT_TIMEZONE, UTF8, LATIN1, \
    DEFAULT_COMPRESS_LEVEL


def zlib(
    text: str,
    encoding: str = UTF8,
    level: int = DEFAULT_COMPRESS_LEVEL
) -> str:
    """
    zlib压缩
    """
    return zcompress(text.encode(encoding), level).decode(LATIN1)


def unzlib(
    text: str,
    encoding: str = UTF8,
) -> str:
    """
    zlib解压
    """
    return zdecompress(text.encode(LATIN1)).decode(encoding)


def gzip(
    text: str,
    encoding: str = UTF8,
    level: int = DEFAULT_COMPRESS_LEVEL
) -> str:
    """
    gzip压缩
    """
    return gcompress(text.encode(encoding), level).decode(LATIN1)


def ungzip(
    text: str,
    encoding: str = UTF8,
) -> str:
    """
    gzip解压
    """
    return gdecompress(text.encode(LATIN1)).decode(encoding)


def encrypt_md5(text: str, encoding: str = UTF8) -> str:
    """
    md5加密
    """
    m = md5()
    m.update(text.encode(encoding))
    return m.hexdigest()


def encrypt_sha1(text: str, encoding: str = UTF8) -> str:
    """
    sha1加密
    """
    sha = sha1()
    sha.update(text.encode(encoding))
    return sha.hexdigest()


def encrypt_sha256(text: str, encoding: str = UTF8) -> str:
    """
    sha256加密
    """
    sha = sha256()
    sha.update(text.encode(encoding))
    return sha.hexdigest()


def bytes2str(data, encoding='utf-8'):
    """
    将bytes数据转换为str
    """
    if isinstance(data, dict):
        return {bytes2str(key): bytes2str(val) for key, val in data.items()}
    elif isinstance(data, list):
        return list(bytes2str(item) for item in data)
    elif isinstance(data, set):
        return set(bytes2str(item) for item in data)
    elif isinstance(data, tuple):
        return tuple(bytes2str(item) for item in data)
    elif isinstance(data, bytes):
        return data.decode(encoding)
    else:
        return data


def tightly_dumps(data):
    """
    json序列化
    分隔符为(",", ":")
    """
    return json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False
    )


def updated_data(data, ori_data):
    """
    有更新的数据
    :param data: 新数据
    :param ori_data: 老数据
    :return 被更新的数据 dict
    """
    updated = dict()
    for key, value in data.items():
        if str(value) != str(ori_data.get(key)):
            updated[key] = value
    if updated:
        logger.debug("data updated: %s" % tightly_dumps({
            "updated": updated,
            "new_data": data,
            "ori_data": ori_data
        }))
    return updated


def contains_chinese(text: str):
    """
    判断字符串是否包含中文
    """
    for char in text:
        if u"\u4e00" <= char <= u"\u9fa5":
            return True
    return False


def timestamp(level=0) -> int:
    """
    获取时间戳
    param level: 级别 默认为秒，level的值每加1结果增加3位
    """
    return int(time.time() * 1000 ** level)


def now_datetime(timezone=DEFAULT_TIMEZONE):
    """
    获取当前的时间
    param timezone: 时区   example: 北京时间：8  美国时间：-4
    """
    # 默认取服务器的时间
    if timezone == DEFAULT_TIMEZONE:
        return datetime.now()
    now = datetime.utcnow()
    return now + timedelta(hours=timezone)


def timeit(func):
    def wrapper(*args, **kwargs):
        st = time.time()
        ret = func(*args, **kwargs)
        logger.warn("func %s timeconsuming %.2f seconds" % (
            func.__name__, time.time() - st)
        )
        return ret
    return wrapper


def async_timeit(func):
    async def wrapper(*args, **kwargs):
        st = time.time()
        ret = await func(*args, **kwargs)
        logger.warn("func %s timeconsuming %.2f seconds" % (
            func.__name__, time.time() - st)
        )
        return ret
    return wrapper
