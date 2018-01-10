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
    uid, cid = trans_int(uid, cid)
    if uid is None or cid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    mongo_models.JianTrack.store_track_cid(uid, cid)
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)
