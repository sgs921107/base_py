##############################################
# 基于centos7、python3构建scrapy、scrapyd运行环境
# 构建命令: 在Dockerfile文件目录下执行 docker build -t centos7-python3-scrapyd .
# 容器启动命令: docker run -dit --name scrapyd --restart=always --privileged=true centos7-py3-scrapyd
# 进入容器：docker exec -it scrapyd /bin/bash
##############################################
FROM centos:7.6.1810
# 指定作者信息
LABEL maintaniner="yiming"
# 配置pip源
COPY ./pip.conf /root/.pip/pip.conf
RUN set -ex \
    # 预安装所需组件
    && yum install -y epel-release \
    && yum install -y wget tar unzip libffi-devel librdkafka-devel zlib-devel bzip2-devel libevent-devel \
        openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make initscripts \
        vim cronie lrzsz rsyslog git net-tools lsof telnet nload iftop ntpdate bash-completion \
    && yum install -y deltarpm \
    && echo "alias vi=vim" >> /root/.bashrc \
    && yum clean all && rm -rf /var/cache/yum/* && rm -rf /tmp/*
 
# 基础环境配置
RUN set -ex \
    # 修改系统时区为东八区
    && rm -rf /etc/localtime \
    && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
 
# 支持中文
RUN set -ex \
    &&yum install -y kde-l10n-Chinese \
    && yum clean all && rm -rf /var/cache/yum/* && rm -rf /tmp/*
RUN localedef -c -f UTF-8 -i zh_CN zh_CN.utf8
ENV LC_ALL=zh_CN.UTF-8 LAN=zh_CN.UTF-8G

# 配置rsyslog 配置当未使用所有权限启动容器时仍可以收集日志
RUN set -ex \
    && mv /etc/rsyslog.d/listen.conf /etc/rsyslog.d/listen.conf.backup \
    && sed -i 's/^$ModLoad imjournal/# $ModLoad imjournal/' /etc/rsyslog.conf \
    && sed -i 's/^$OmitLocalLogging on/$OmitLocalLogging off/' /etc/rsyslog.conf \
    && sed -i 's/^$IMJournalStateFile imjournal.state/# $IMJournalStateFile imjournal.state/' /etc/rsyslog.conf
 
# 配置python3环境
RUN set -ex \
    && yum install -y python-devel python-pip python3-devel python3-3.6.8 \
    && python2 -m pip install --upgrade pip==19.0.3 \
    # 删除旧版本python环境变量
    && rm -f /usr/bin/python \
    && rm -f /usr/bin/pip \
    # 配置默认为python3
    && ln -s /usr/bin/python3 /usr/bin/python \
    && ln -s /usr/bin/pip3 /usr/bin/pip \
    # 修复因修改python版本导致yum失效问题
    && sed -i "s#/usr/bin/python#/usr/bin/python2#" /usr/bin/yum \
    && sed -i "s#/usr/bin/python#/usr/bin/python2#" /usr/libexec/urlgrabber-ext-down \
    && python -m pip install --upgrade pip \
    && python -m pip install --upgrade setuptools==50.3.2 \
    && yum clean all && rm -rf /var/cache/yum/* && rm -rf /tmp/*


# 安装golang环境
# RUN set -ex \
#     && yum install -y golang vim-go \
#     && go env -w GO111MODULE=auto \
#     && go env -w GOPROXY=https://goproxy.io,direct \
#     && go env -w GOPRIVATE=*.gitlab.com,*.gitee.com \
#     && go env -w GOSUMDB=sum.golang.google.cn \
#     && mkdir /usr/share/vim/vimfiles/templates \
#     && touch /usr/share/vim/vimfiles/templates/hello_world.go \
#     && yum clean all && rm -rf /var/cache/yum/* && rm -rf /tmp/*
 
# 安装python爬虫依赖库
COPY ./requirements.txt /tmp/requirements.txt
# pycrypto不能正常使用需要卸载重新安装
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip uninstall -y pycrypto \
    && pip install pycrypto==2.6.1
 
# 配置vim
# COPY ./vimrc /root/.vimrc
 
RUN mkdir /scrapyd_work
WORKDIR /scrapyd_work
 
EXPOSE 6800
EXPOSE 5000
 
CMD ["/bin/bash", "-c", "rsyslogd | crond | `logparser -dir /scrapyd_work/logs` | rm twistd.pid | scrapyd"]