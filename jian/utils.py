#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import logging
from datetime import datetime, timedelta
from collections import Counter
import pymongo

from qingdian_jian.utils import get_mongo_collection

logger = logging.getLogger(__name__)
TRACK_COLLECTION_NAME = 'jian_track'
TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'
JIAN_HISTORY_COLLECTION_NAME = 'jian_history'


def store_tuijian_history(uid: int, jian_cids: list):
    """
    将推荐过的存储记录，下次不再推荐推荐过的
    :param uid:
    :param jian_cids:
    :return:
    """
    data = {'uid': uid, 'jids': jian_cids, 'update_time': datetime.now()}
    db = get_mongo_collection(JIAN_HISTORY_COLLECTION_NAME)
    db.insert_one(data)
    logger.debug(f'存储推荐记录{data}')


def get_jian_history(uid: int, begin=None, end=None):
    db = get_mongo_collection(JIAN_HISTORY_COLLECTION_NAME)
    history = []
    hs = db.find({'uid': uid}).sort('update_time', pymongo.DESCENDING)
    for h in hs:
        history += h['jids']
    if begin is not None and end is not None:
        history = history[begin:end]
    logger.debug(f'获取到推荐过的历史 {history}')
    return history


def get_trackcids_tracktids(uid: int):
    db = get_mongo_collection(TRACK_COLLECTION_NAME)
    trackcids = []
    tracktids = []
    for t in db.find({'uid': uid}).sort('update_time', pymongo.DESCENDING):
        trackcids.append(t['cid'])
        tracktids += t['tids']
    trackcids = list(set(trackcids))
    tracktids = list(set(tracktids))
    logger.debug(f'获取到埋点记录trackcids= {trackcids}, trackedtids= {tracktids}')
    return trackcids, tracktids


def get_track_disscids_diss_tids(uid: int):
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    diss_cids = []
    diss_tids = []
    for d in db.find({'uid': uid}).sort('update_time', pymongo.DESCENDING):
        diss_cids.append(d['cid'])
        diss_tids += d['tids']
    diss_cids = list(set(diss_cids))
    diss_tids = list(set(diss_tids))
    logger.debug(f'获取不喜欢记录diss_cids={diss_cids}, diss_tids={diss_tids}')
    return diss_cids, diss_tids


def get_recently_hot_tracked(recent_days=2, limit=20, nocids=None):
    recent = datetime.now() - timedelta(days=recent_days)
    if nocids is None:
        nocids = []
    db = get_mongo_collection(TRACK_COLLECTION_NAME)
    recent_tracked_cids = []
    curor = db.find({'update_time': {'$gte': recent}, 'cid': {'$nin': nocids}}).sort('update_time', pymongo.DESCENDING)
    for t in curor:
        recent_tracked_cids.append(t['cid'])
    c = Counter(recent_tracked_cids)
    most_common = c.most_common(limit)
    sum_most_common = sum([i[1] for i in most_common])
    cid_sim_list = [(m[0], m[1] / sum_most_common) for m in most_common]
    return cid_sim_list


if __name__ == '__main__':
    d = get_recently_hot_tracked(limit=5, nocids=[1455, 729])
    print(d)
