#!/usr/bin/env bash

APP_NAME='qingdian_jian'

# 起
echo "starting $APP_NAME"
/root/envs/qingdian_jian/bin/gunicorn -D -w 4 -b :9000 qingdian_jian.wsgi
echo "started"