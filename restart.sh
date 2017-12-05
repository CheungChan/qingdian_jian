#!/usr/bin/env bash

# 杀
pgrep gunicorn|xargs kill
# 起
/root/envs/qingdian_jian/bin/gunicorn -D -w 4 -b :9000 qingdian_jian:wsgi