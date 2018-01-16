#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging

from django.http import JsonResponse

from jian import mongo_models
from qingdian_jian.utils import type_cast_request_args, log_views

logger = logging.getLogger(__name__)


@log_views
def track(request):
    """
    用户调用存储喜欢内容的动作
    :param request:
    :return:
    """
    validaters = [('uid', 0, int),
                  ('cid', 0, int),
                  ('client', 0, int),
                  ('device_id', None, str),
                  ('behavior', 0, int)]
    uid, cid, client, device_id, behavior = type_cast_request_args(request, validaters)
    if any((x is None for x in [uid, cid, client, behavior, device_id])):
        j = {'status': -1, 'msg': '参数传递非法'}
        logger.error(j)
        return JsonResponse(j, safe=False)
    mongo_models.JianTrack.store_track_cid(uid, cid, client, behavior, device_id)
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)
