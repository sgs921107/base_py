#!/usr/bin/env python
# -*- coding=utf8 -*-
import os
if __name__ != '__main__':
    import sys
    CUR_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(CUR_DIR)
    sys.path.insert(0, PROJECT_DIR)
    sys.path.insert(0, CUR_DIR)

from alembic.config import Config

from utils.orm import DB

# db仓库地址
REPO_PATH = os.path.join(PROJECT_DIR, "db_repository")
# 迁移工具配置文件地址 初始化仓库时的依赖 以后不使用此配置
CONFIG_FILE = "/tmp/alembic.ini"
# 迁移版本管理表
# MIGRATE_VERSION_TABLE = "migrate_version"


def get_alembic_config(file_: str = None):
    config = Config(file_=file_)
    config.set_main_option("sqlalchemy.url", DB.create_url(sync=False))
    config.set_main_option("script_location", REPO_PATH)
    config.set_main_option("prepend_sys_path", PROJECT_DIR)
    return config
