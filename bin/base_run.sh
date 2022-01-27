#!/usr/bin/env bash

CMDS_DIR="$PROJECT_DIR/bin"

# env管理脚本
env_manager="$CMDS_DIR/env_manager.py"
# 复制env管理脚本到/projects目录下(原文件不具有操作权限)
real_manager="/projects/env_manager.py"
cp $env_manager $real_manager
# 给操作env配置文件的脚本所有的权限
chmod 777 $real_manager
# 给操作env配置文件的脚本添加快捷方式
rm -f /usr/bin/envm && ln -s $real_manager /usr/bin/envm
