#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import logging
import time
from functools import wraps

import pymongo
import redis

from qingdian_jian import settings

logger = logging.getLogger(__name__)
pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
r = None


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
        logger.info(f.__name__ + settings.LOG_BEGIN)
        r = f(*args, **kwargs)
        end = time.time()
        logger.info(f.__name__ + settings.LOG_END + f' at {end-start}s')
        return r

    return wrapper


if __name__ == '__main__':
    r = get_redis()
    # r.set('test_chenzhang','测试',10)
    # print(r.get('test_chenzhang').decode('utf-8'))
