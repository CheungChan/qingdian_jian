#!/usr/bin/env bash

# 配置
APP_NAME='qingdian_jian'
PORT=9000

# 检测
if [ -z "$WORKON_HOME" ]
then
    echo '$WORKON_HOME 环境变量未设置,请安装virtualenv virtualenvwrapper 并设置环境变量$WORKON_HOME'
    exit -1
fi

# 装依赖
echo '安装依赖'
"$WORKON_HOME"/"$APP_NAME"/bin/pip install -r requirements.txt
echo "依赖安装完成"

# 杀
echo "尝试停止 $APP_NAME"
echo "运行中的任务:"
ps aux|grep ${APP_NAME}|grep -v 'grep'
if [ $? -ne 0 ]
then
    echo "**** $APP_NAME 未运行"
else
    ps aux|grep ${APP_NAME}|grep -v 'grep'|awk '{print $2}'|xargs kill
    echo "**** $APP_NAME 终止成功"
fi

# 起
echo "尝试开启 $APP_NAME"
"$WORKON_HOME"/"$APP_NAME"/bin/gunicorn -D -w 4 -b :"$PORT" "$APP_NAME".wsgi
echo "**** $APP_NAME 启动成功"