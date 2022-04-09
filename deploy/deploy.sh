#!/usr/bin/env bash
###
 # @Description: 项目部署脚本
### 

########################### 注意事项 ############################
# todo 替换所有py_framework为项目名称
# 1.手动clone代码并切换至目标分支或标签
# 2.根据configs/env_demo生成并配置env文件/etc/py_framework/.env
# 3.root用户运行: source /etc/py_framework/.env && cd $HOST_PROJECT_DIR/deploy && sh deploy.sh
################################################################

echo "====================== begin deploy ========================="

# -----------------------------------------------------------------
# 宿主机的env配置文件所在的目录
HOST_ENV_PATH=/etc/py_framework/.env

source $HOST_ENV_PATH

# 部署目录
DEPLOY_DIR=$HOST_PROJECT_DIR/deploy
# docker-compose配置文件
COMPOSE_ENV_PATH=$DEPLOY_DIR/.env
# 安装docker的脚本
DOCKER_INSTALLER=install_docker.sh

# -------------------------------- 开始部署 --------------------------

# 进入部署目录
cd $DEPLOY_DIR || { echo "部署失败: 进入项目部署目录失败, 请校验您的分支是否正确"; exit 1; }

# 检查是否已安装docker服务
sh $DOCKER_INSTALLER || { echo "部署失败: 安装docker服务失败,请检查是否缺少依赖并重新运行部署脚本"; exit 1; }

# 将项目env配置链接至deploy/.env
ln -f $HOST_ENV_PATH $COMPOSE_ENV_PATH

# 拉取镜像
# 检查是否配置了docker仓库
if [ "$HOST_DOCKER_REPOSITORY" != "" ]
then
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
fi
# 开始拉取镜像, 如果拉取失败则直接构建
docker pull $HOST_DOCKER_REPOSITORY/$COMEPOSE_IMAGE_NAME:latest \
    && docker tag $HOST_DOCKER_REPOSITORY/$COMEPOSE_IMAGE_NAME:latest $IMAGE_NAME:latest \
    || { \
        echo "拉取镜像失败, 开始构建镜像"; docker-compose build \
        && echo "构建镜像完成, 请手动上传镜像: docker tag $COMEPOSE_IMAGE_NAME:latest $HOST_DOCKER_REPOSITORY/$IMAGE_NAME:latest && docker push $HOST_DOCKER_REPOSITORY/$IMAGE_NAME:latest" \
        || { \
            echo "部署失败: 构建镜像失败"; exit 1; \
        }; 
    }
# 删除产生的<none>镜像
none_imgs=$(docker images | grep '<none>' | awk '{print $3}')
if [ "$none_imgs" != "" ]
then
    docker rmi $none_imgs
fi

# 初始化命令
# 执行迁移
# docker-compose run --rm demo python db_manager.py upgrade head

# 执行单元测试

# 启动服务
for service in demo web nginx logrotate
do
    scale_name=`echo service_"$service"_scale | tr a-z A-Z`
    scale=$(eval echo \$$scale_name)
    if [ "$scale" != "0" ]
    then
        docker-compose up --scale $service=$scale -d $service \
        && { echo "启动"$service"服务成功"; docker-compose logs  --tail 10 $service; } \
        || echo "启动服务"$service"失败!!!"
    fi
done

echo "====================== deploy done ========================="
