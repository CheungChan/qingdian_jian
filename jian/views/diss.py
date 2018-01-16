#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging

from django.http import JsonResponse

from jian import mongo_models
from qingdian_jian.utils import trans_int, log_views

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
    client = request.GET.get('client', 0)
    device_id = request.GET.get('device_id')
    uid, cid, client = trans_int(uid, cid, client)
    if any((x is None for x in [uid, cid, client, device_id])):
        j = {'status': -1, 'msg': '参数传递非法', 'query': request.GET}
        logger.error(j)
        return JsonResponse(j, safe=False)
    mongo_models.JianTrackDiss.store_diss_cid(uid, cid, client, device_id)
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
    client = request.GET.get('client', 0)
    device_id = request.GET.get('device_id')
    uid, tid, client = trans_int(uid, tid, client)
    if any((x is None for x in [uid, tid, client, device_id])):
        j = {'status': -1, 'msg': '参数传递非法', 'query': request.GET}
        logger.error(j)
        return JsonResponse(j, safe=False)
    mongo_models.JianTrackDiss.store_diss_tid(uid, tid, client, device_id)
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
        logger.error(j)
        return JsonResponse(j, safe=False)
    records = mongo_models.JianTrackDiss.get_track_disscids_diss_tids(uid)[0]
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
        j = {'status': -1, 'msg': '参数传递非法', 'data': []}
        logger.error(j)
        return JsonResponse(j, safe=False)
    records = mongo_models.JianTrackDiss.get_track_disscids_diss_tids(uid)[1]
    records = list(set(records))
    j = {'status': 0, 'data': records}
    logger.info(f'diss_theme_list j={j}')
    return JsonResponse(j, safe=False)
