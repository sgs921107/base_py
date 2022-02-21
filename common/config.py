#!/usr/bin/env python
# -*- coding=utf8 -*-

import logging.config
from typing import Any
from os import environ, path
from pydantic import BaseModel, Field

from dotenv.main import DotEnv

from common.conts import DEFAULT_LOG_FORMAT, ENV_PATH, \
    DEFAULT_LOG_DATEFMT, DEVELOP


class Config(BaseModel):
    # redis
    # 项目使用的redis key的前缀
    redis_prefix: str = "pyp"
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    redis_mode: str = ""
    redis_db: int = Field(default=0, ge=0, le=15)
    redis_password: str = ""

    # mysql
    mysql_prefix: str = "pyp"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3006
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_db: str = "test_db"
    mysql_charset: str = "utf8mb4"
    mysql_pool_size: int = 30

    # rabbitmq
    rabbitmq_host: str = "127.0.0.1"
    rabbitmq_port: int = 5672
    rabbitmq_username: str = "test"
    rabbitmq_password: str = "123456"
    rabbitmq_vhost: str = "/"
    rabbitmq_heartbeat: int = 10

    # 日志
    log_level: str = "DEBUG"
    log_format: str = DEFAULT_LOG_FORMAT
    # 服务配置
    srv_timeout: float = 30
    srv_environment: str = "product"

    @classmethod
    def load_envs(cls, env_path=ENV_PATH, encoding="utf-8"):
        """
        加载env然后返回一个config实例
        """
        if not path.isfile(env_path):
            raise ValueError("%s no exist or not a file" % env_path)
        env_manager = DotEnv(
            dotenv_path=env_path, verbose=True, encoding=encoding
        )
        sys_envs = dict(environ.copy())
        envs = env_manager.dict()
        sys_envs.update(envs)
        return cls(**sys_envs)

    @classmethod
    def get_instance(cls):
        """
        获取config实例，单例
        """
        if not hasattr(cls, "instance"):
            setattr(cls, "instance", cls.load_envs())
        return getattr(cls, "instance")

    def get(self, configuration, default: Any = None):
        if hasattr(self, configuration):
            return getattr(self, configuration)
        else:
            self.get_logger().warning(
                "Try to get an unexpected option: %s" % configuration
            )
            return default

    @classmethod
    def get_logger(cls):
        if not hasattr(cls, "logger"):
            config: cls = cls.get_instance()
            log_level = config.log_level.upper()
            logging_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        'format': config.log_format,
                        'datefmt': DEFAULT_LOG_DATEFMT
                    }
                },

                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "DEBUG",
                        "formatter": "default",
                        "stream": "ext://sys.stdout"
                    },
                },

                "loggers": {
                    "simple": {
                        'handlers': ['console'],
                        'level': log_level,
                        'propagate': False
                    }
                },

                "root": {
                    'handlers': ['console'],
                    'level': config.srv_environment == DEVELOP and log_level or "WARNING",
                }
            }
            logging.config.dictConfig(logging_config)
            setattr(cls, "logger", logging.getLogger("simple"))
        return getattr(cls, "logger")
