#!/usr/bin/env bash

# 杀
APP_NAME='qingdian_jian'
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
~/envs/qingdian_jian/bin/gunicorn -D -w 4 -b :9000 qingdian_jian.wsgi
echo "**** $APP_NAME 启动成功"