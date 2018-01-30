#!/usr/bin/env bash
#set -e

# 配置
APP_NAME='qingdian_jian'
PORT=9000

# 检测
if [ -z "$WORKON_HOME" ]
then
    echo '$WORKON_HOME 环境变量未设置,请安装virtualenv virtualenvwrapper 并设置环境变量$WORKON_HOME'
    exit -1
fi
VIRTUAL_ENV_PYTHON_HOME="$WORKON_HOME"/"$APP_NAME"
if [ ! -d "$VIRTUAL_ENV_PYTHON_HOME" ]
then
    echo "$VIRTUAL_ENV_PYTHON_HOME 虚拟环境未创建,请先创建虚拟环境,再尝试运行"
    echo "命令参考: mkvirtualenv $APP_NAME -p python3.6"
    exit -1
fi

# 装依赖
echo '安装依赖'
"$VIRTUAL_ENV_PYTHON_HOME"/bin/pip install -r requirements.txt || (echo "依赖安装失败"; exit -1)
echo "依赖安装完成"

# 杀
echo "尝试停止 $APP_NAME"
echo "运行中的任务:"
ps aux|grep "$APP_NAME"|grep -v 'grep'
if [ $? -ne 0 ]
then
    echo "**** $APP_NAME 未运行"
else
    ps aux|grep ${APP_NAME}|grep -v 'grep'|awk '{print $2}'|xargs kill
    echo "**** $APP_NAME 终止成功"
fi

# 起
echo "尝试开启 $APP_NAME"
"$VIRTUAL_ENV_PYTHON_HOME"/bin/gunicorn -D -w 4 -b :"$PORT" "$APP_NAME".wsgi || (echo "启动失败"; exit -1)
echo "**** $APP_NAME 启动成功"