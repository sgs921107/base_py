#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: common
'''

# from dataclasses import dataclass

from common.config import Config

logger = Config.get_logger()
config: Config = Config.get_instance()


def real_key(key: str) -> str:
    if config.redis_prefix.endswith(":"):
        return config.redis_prefix + key
    return ":".join([config.redis_prefix, key])


# @dataclass
class RedisKey:
    test_hash = real_key("test_hash")


if __name__ == '__main__':
    pass
