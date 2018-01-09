#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging
from datetime import datetime

from django.http import JsonResponse

from jian import models
from qingdian_jian.utils import get_mongo_collection, trans_int, log_views

TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'
TRACK_DISS_THEME_COLLECTION_NAME = 'jian_track_diss_theme'
logger = logging.getLogger(__name__)


@log_views
def track_diss(request):
    """
    用户调用存储不喜欢内容。
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    uid, cid = trans_int(uid, cid)
    if uid is None or cid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    data = {'uid': uid, 'cid': cid}
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    if db.count(data) == 0:
        tags = models.ContentsTag.get_tids_by_cid(cid)
        data.update({'tids': tags, 'update_time': datetime.now()})
        db.insert_one(data)
        logger.info(f'插入，track_diss data={data}')
    else:
        logger.error(f'已存在， track_diss data={data}')
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)


@log_views
def track_diss_theme(request):
    """
    用户调用存储不喜欢主题
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    tid = request.GET.get('tid')
    uid, tid = trans_int(uid, tid)
    if uid is None or tid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    db = get_mongo_collection(TRACK_DISS_THEME_COLLECTION_NAME)
    data = {'uid': uid, 'tid': tid}
    if db.count(data) == 0:
        data.update({'update_time': datetime.now()})
        db.insert_one(data)
        logger.info(f'插入，track_diss_theme data={data}')
    else:
        logger.error(f'已存在， track_diss_theme data={data}')
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)


@log_views
def diss_list(request):
    """
    用户查询不喜欢内容的列表
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    uid, = trans_int(uid)
    if uid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    records = []
    for r in db.find({'uid': uid}):
        records.append(r['cid'])
    records = list(set(records))
    j = {'status': 0, 'data': records}
    logger.info(f'diss_list j={j}')
    return JsonResponse(j, safe=False)


@log_views
def diss_theme_list(request):
    """
    用户查询用户不喜欢主题的列表。
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    uid, = trans_int(uid)
    if uid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    db = get_mongo_collection(TRACK_DISS_THEME_COLLECTION_NAME)
    records = []
    for r in db.find({'uid': uid}):
        records.append(r['tid'])
    records = list(set(records))
    j = {'status': 0, 'data': records}
    logger.info(f'diss_theme_list j={j}')
    return JsonResponse(j, safe=False)
