### 
 # @Author: xiangcai
 # @Date: 2022-04-20 09:58:50
 # @LastEditors: xiangcai
 # @LastEditTime: 2022-04-21 14:03:49
 # @Description: file content
### 
echo "---------------------开始重启服务---------------------"
# 宿主机的env配置文件所在的目录
HOST_ENV_PATH=/etc/py_framework/.env

source $HOST_ENV_PATH

# 启动服务
for service in demo web nginx logrotate
do
    scale_name=`echo service_"$service"_scale | tr a-z A-Z`
    scale=$(eval echo \$$scale_name)
    if [ "$scale" != "0" ]
    then
        docker-compose restart $service \
        && { sleep 2; echo "重启"$service"服务成功"; docker-compose logs  --tail 10 $service; } \
        || echo "启动服务"$service"失败!!!"
    fi
done
echo "---------------------重启服务结束---------------------"