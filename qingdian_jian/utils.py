#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Dict

import pymongo
import redis
from bson.objectid import ObjectId
from logzero import logger

from qingdian_jian import settings

pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
r = None
global_connection = None
# 无效的cid
no_cids = [None, 0, 1]


def get_redis():
    global r
    if not r:
        r = redis.Redis(connection_pool=pool)
    return r


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
        logger.info(settings.LOG_END)
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


def cache_redis(redis_key: str, cache_seconds: int = None, json_dump=False):
    """
    缓存到redis
    :param redis_key:
    :param cache_seconds:
    :param json_dump: 如果结果需要json.dumps,则设为True
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            value = get_redis().get(redis_key)
            if value:
                logger.debug(f'从缓存中取出{redis_key}')
                if json_dump:
                    return json.loads(value.decode('utf-8'))
                else:
                    return value.decode('utf-8')
            result = func(*args, **kwargs)
            if json_dump:
                value = json.dumps(result)
            logger.debug(f'设置缓存{redis_key}')
            get_redis().set(redis_key, value, ex=cache_seconds)
            return result

        return wrapper

    return decorator


def jsonKeys2int(x: Dict[str, object], layer=1):
    result = {}
    if layer == 1:
        result = {int(k): v for k, v in x.items()}
    else:
        for k, v in x.items():
            result[int(k)] = jsonKeys2int(v, layer=layer - 1)
    return result


def jsonKeys2str(x: Dict[str, object], layer=1):
    result = {}
    if layer == 1:
        result = {str(k): v for k, v in x.items()}
    else:
        for k, v in x.items():
            result[int(k)] = jsonKeys2str(v, layer=layer - 1)
    return result


if __name__ == '__main__':
    r = get_redis()
    # request = MockRequest('1', None, None)
    # mock_index(request)
    # r.set('azhang_test', 'value', ex=5 * 60)
    # print(r.get('azhang_test'))
    # db = get_mongo_collection("content_similarity_offline")
    # keys = [k.decode('utf-8') for k in r.keys('azhang_jian_simi_*')]
    # for k in keys:
    #     v = r.get(k).decode('utf-8')
    #     v = json.loads(v)
    #     k = k.replace('azhang_jian_simi_', '')
    #     data = {'cid': k, 'cid2_sim': v}
    #     db.insert(data)
    #     print(data)
    x = {'4': {'1': {'1': 3.14, '2': 34}, '2': {'4': 56}}}
    print(jsonKeys2int(x, layer=3))
