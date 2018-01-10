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
    uid, cid = trans_int(uid, cid)
    if uid is None or cid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    mongo_models.JianTrackDiss.store_diss_cid(uid, cid)
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
    mongo_models.JianTrackDiss.store_diss_tid(uid, tid)
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
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    records = mongo_models.JianTrackDiss.get_track_disscids_diss_tids(uid)[1]
    records = list(set(records))
    j = {'status': 0, 'data': records}
    logger.info(f'diss_theme_list j={j}')
    return JsonResponse(j, safe=False)
