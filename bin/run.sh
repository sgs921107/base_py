#!/usr/bin/env bash
###
 # @Description: 启动脚本
### 

/bin/bash base_run.sh

circus_conf="$PROJECT_DIR/configs/circus.ini"
circusd $circus_conf
