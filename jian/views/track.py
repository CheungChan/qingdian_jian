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
def track(request):
    """
    用户调用存储喜欢内容的动作
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    client = request.GET.get('client', 0)
    device_id = request.GET.get('device_id', 0)
    behavior = request.GET.get('behavior', 0)
    uid, cid, client, behavior = trans_int(uid, cid, client, behavior)
    if any((x is None for x in [uid, cid, client, behavior, device_id])):
        j = {'status': -1, 'msg': '参数传递非法'}
        logger.error(j)
        return JsonResponse(j, safe=False)
    mongo_models.JianTrack.store_track_cid(uid, cid, client, behavior, device_id)
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)
