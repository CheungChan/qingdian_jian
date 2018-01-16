#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import logging
import time
import json
from functools import wraps
from datetime import datetime
import pymongo
from bson.objectid import ObjectId
import redis

from qingdian_jian import settings

logger = logging.getLogger(__name__)
pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
r = None
# 无效的cid
no_cids = [None, 0, 1]


def get_redis():
    global r
    if not r:
        r = redis.Redis(connection_pool=pool)
    return r


global_connection = None


def get_connection():
    global global_connection
    if not global_connection:
        global_connection = pymongo.MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
    return global_connection


def get_mongo_collection(collection_name):
    connection = get_connection()
    database = connection[settings.MONGO_DATABASE]
    return database[collection_name]


def trans_int(*param, error_return=None):
    int_param = []
    for p in param:
        try:
            p = int(p)
            int_param.append(p)
        except (ValueError, TypeError):
            return [error_return for _ in param]
    return int_param


def override(f):
    """
    装饰器，提醒属于override的方法。
    :param f:
    :return:
    """
    return f


def log_views(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = time.time()
        request = args[0]
        path = request.get_full_path()
        logger.info(settings.LOG_BEGIN + path)
        r = f(*args, **kwargs)
        end = time.time()
        logger.info(settings.LOG_END + path)
        logger.info(f'{end-start} s')
        return r

    return wrapper


class MongoDocEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


def filter_cids(cids):
    return list(set(list(filter(lambda x: x not in no_cids, cids))))


def type_cast_request_args(request, validates, method='GET'):
    return_list = []
    for v in validates:
        arg_name = v[0]
        arg_default = v[1]
        arg_type = v[2]

        if method == 'GET':
            arg_method = request.GET
        elif method == 'POST':
            arg_method = request.POST
        else:
            raise Exception('方法只支持GET和POST请求')

        arg = arg_method.get(arg_name, arg_default)
        if arg is None:
            arg = arg_default
        else:
            try:
                arg = arg_type(arg)
            except (ValueError, TypeError) as e:
                arg = arg_default
        return_list.append(arg)
    return return_list


class MockRequest:
    def __init__(self, a, b, c):
        print('init reqeust')
        self.GET = dict()
        self.GET['a'] = a
        self.GET['b'] = b
        self.GET['c'] = c


def mock_index(request):
    validates = [('a', 0, int),
                 ('b', 0.0, float),
                 ('c', '', str)]
    a, b, c = type_cast_request_args(request, validates)
    print(a, b, c)
    print(type(a), type(b), type(c))
    return 'hello world'


if __name__ == '__main__':
    r = get_redis()
    request = MockRequest('1', None, None)
    mock_index(request)
