#!/usr/bin/env bash
###
 # @Description: 项目部署脚本
### 

########################### 注意事项 ############################
# todo 替换$HOST_CONF_DIR为具体路径
# 1.手动clone代码并切换至目标分支或标签
# 2.根据configs/env_demo生成并配置env文件$HOST_CONF_DIR/.env
# 4.root用户运行: source $HOST_CONF_DIR/.env && cd $HOST_PROJECT_DIR/deploy && sh deploy.sh
################################################################

echo "====================== begin deploy ========================="

# -----------------------------------------------------------------
# todo 替换以下base_pyp为项目名字
# 避免多个项目网络配置冲突
COMPOSE_PROJECT_NAME=base_pyp
# 宿主机的env配置文件所在的目录
HOST_CONF_DIR=/etc/base_pyp
# 容器内的项目目录
PROJECT_DIR=/projects/base_pyp
# 容器内配置文件路径
PROJECT_ENV=/etc/base_pyp/.env
# 容器内的日志目录
LOG_DIR=/var/log/base_pyp
# 镜像名字
IMAGE_NAME=base_pyp

source $HOST_CONF_DIR/.env

# 部署目录
deploy_dir=$HOST_PROJECT_DIR/deploy
# docker-compose配置文件
docker_compose_env=$deploy_dir/.env
# 安装docker的脚本
install_docker_script=$deploy_dir/install_docker.sh

# -------------------------------- 开始部署 --------------------------

# 进入项目目录
cd $HOST_PROJECT_DIR || { echo "部署失败: 进入项目目录失败, 请检查env配置"; exit 1; }

# 进入部署目录
cd $deploy_dir || { echo "部署失败: 进入项目部署目录失败, 请校验您的分支是否正确"; exit 1; }

# 检查是否已安装docker服务
sh $install_docker_script || { echo "部署失败: 安装docker服务失败,请检查是否缺少依赖并重新运行部署脚本"; exit 1; }

# 生成docker-compose.yml依赖变量的.env文件
echo "COMPOSE_PROJECT_NAME=$COMPOSE_PROJECT_NAME
HOST_CONF_DIR=$HOST_CONF_DIR
HOST_LOG_DIR=$HOST_LOG_DIR
PROJECT_DIR=$PROJECT_DIR
PROJECT_ENV=$PROJECT_ENV
LOG_DIR=$LOG_DIR
IMAGE_NAME=$IMAGE_NAME" > $docker_compose_env

# 拉取镜像
# 配置允许使用http访问私有仓库
echo "是否配置允许使用http访问私有docker镜像仓库，请选择操作："
echo "1: 是  将进行配置并重启docker服务"
echo "2: 否  忽略并继续部署(请确保您的私有仓库允许https访问 或已手动配置)"
echo "请输入（选项1或2）："
read choice
# 校验选择是否预期
while [ "$choice" != "1" ] && [ "$choice" != "2" ]
do
    echo "不期望的选择: $choice, 请重新输入"
    read choice
done
if [ "$choice" = "1" ]
then
    echo "开始配置"
    # 判断是否已存在配置文件, 则进行备份
    if [ -f "/etc/docker/daemon.json" ]
    then
        cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
    fi
    echo "{\"insecure-registries\":[\"$HOST_DOCKER_REPOSITORY\"]}" > /etc/docker/daemon.json
    echo "配置完成, 开始重启docker服务"
    sudo systemctl daemon-reload
    sudo systemctl restart docker
fi
# 开始拉取镜像, 如果拉取失败则直接构建
docker pull $HOST_DOCKER_REPOSITORY/$IMAGE_NAME:latest \
    && docker tag $HOST_DOCKER_REPOSITORY/$IMAGE_NAME:latest $IMAGE_NAME:latest \
    || { \
        echo "拉取镜像失败, 开始构建镜像"; docker-compose build \
        && echo "构建镜像完成, 请手动上传镜像: docker tag $IMAGE_NAME:latest $HOST_DOCKER_REPOSITORY/$IMAGE_NAME:latest && docker push $HOST_DOCKER_REPOSITORY/$IMAGE_NAME:latest" \
        || { \
            echo "部署失败: 构建镜像失败"; exit 1; \
        }; 
    }
# 删除产生的<none>镜像
docker rmi $(docker images | grep '<none>' | awk '{print $3}')

# 执行迁移
# docker-compose run --rm demo python db_manager.py upgrade head

# 执行单元测试

# 启动服务
docker-compose up -d
sleep 3
echo "服务启动日志:"
docker-compose logs --tail 10

echo "====================== deploy done ========================="
