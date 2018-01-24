#!/usr/bin/env bash

# 杀
APP_NAME='qingdian_jian'
echo "stopping $APP_NAME"
ps aux|grep ${APP_NAME}|grep -v 'grep'|awk '{print $2}'|xargs kill
echo "stopped"
# 起
echo "starting $APP_NAME"
/root/envs/qingdian_jian/bin/gunicorn -D -w 4 -b :9000 qingdian_jian.wsgi
echo "started"