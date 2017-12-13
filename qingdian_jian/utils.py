import redis

import pymongo

from qingdian_jian import settings

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
            return error_return
    return int_param


if __name__ == '__main__':
    r = get_redis()
    # r.set('test_chenzhang','测试',10)
    # print(r.get('test_chenzhang').decode('utf-8'))
