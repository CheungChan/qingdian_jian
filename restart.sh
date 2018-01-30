#!/usr/bin/env bash

# 配置
APP_NAME='qingdian_jian'
PORT=9000


# 装依赖
echo '安装依赖'
~/envs/"$APP_NAME"/bin/pip install -r requirements.txt


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
~/envs/"$APP_NAME"/bin/gunicorn -D -w 4 -b :"$PORT" "$APP_NAME".wsgi
echo "**** $APP_NAME 启动成功"