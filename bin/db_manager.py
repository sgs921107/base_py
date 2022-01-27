#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: 数据库迁移管理
等价于alembic命令(不再依赖配置文件alembic.ini)
example:
    自动生成迁移文件: python db_manager.py revision --autogenerate -m "init db" --rev-id v1.0
    执行迁移: python db_manager.py upgrade head
    降级: python db_manager.py downgrade
'''
from __init__ import get_alembic_config

from alembic.config import CommandLine


def main(argv=None, prog=None, **kwargs):
    """
    等价于alembic命令(不再依赖配置文件alembic.ini)
    """
    cmd_line = CommandLine(prog=prog)
    options = cmd_line.parser.parse_args(argv)
    if not hasattr(options, "cmd"):
        # see http://bugs.python.org/issue9253, argparse
        # behavior changed incompatibly in py3.3
        cmd_line.parser.error("too few arguments")
    else:
        config = get_alembic_config()
        cmd_line.run_cmd(config, options)


if __name__ == '__main__':
    main()
