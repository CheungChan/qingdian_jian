#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/23 12:09
# @Author  : 陈章
import gevent
from gevent import monkey
import time
import sys

monkey.patch_socket()
import requests

login_url = 'http://www.qcomic.cc/qdapi/loginByTelPassword'
register_url = 'http://www.qcomic.cc/qdapi/setUserInfoBySmsCode'
checkcode_url = 'http://www.qcomic.cc/qdapi/getSmsCode'
params = {"tel": "13111111111", "code": "111111", "user_name": "123456", "password": "123456"}
checkcode_param = {'tel': "13161159255", 'type': 1}
# with open('out.txt', 'w', encoding='utf-8') as f:
#     sys.stdout = f


def send_register(i):
    resp = requests.post(register_url, params=params)
    print(resp.text)
    print(resp.status_code)
    print(time.time())


def send_checkcode(i):
    print(i)
    resp = requests.post(checkcode_url, params=checkcode_param)
    print(resp.json())


jobs = [gevent.spawn(send_register, i) for i in range(10 ** 4)]
# jobs = [gevent.spawn(send_checkcode, i) for i in range(10)]
gevent.joinall(jobs)
