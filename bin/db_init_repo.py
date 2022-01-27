#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: 初始化仓库(已初始化)
'''
from alembic.command import init

from __init__ import REPO_PATH, CONFIG_FILE, get_alembic_config


def main():
    # 初始化db仓库
    config = get_alembic_config(CONFIG_FILE)
    init(config, REPO_PATH)


if __name__ == '__main__':
    main()
