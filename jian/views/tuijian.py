#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging

from django.http import JsonResponse

from jian import mongo_models
from jian.process import Process
from qingdian_jian.utils import type_cast_request_args, log_views

logger = logging.getLogger(__name__)


@log_views
def cids_by_uid(request):
    """
    用户调用获得推荐
    :param request:
    :return:
    """
    validaters = [('uid', 0, int),
                  ('n', 20, int),
                  ('client', 0, int),
                  ('device_id', None, str)]
    uid, n, client, device_id = type_cast_request_args(request, validaters)
    if any([x is None for x in (uid, n, client, device_id)]):
        j = {'status': -1, 'msg': '参数传递非法', 'data': []}
        logger.error(j)
        return JsonResponse(j, safe=False)
    data, analyze = Process(uid, n, client, device_id)()
    j = {'status': 0, 'data': data, 'analyze': analyze}
    logger.info(f'>>> jian j= {j}')
    return JsonResponse(j, safe=False)


@log_views
def jian_history(request):
    """
    用户调用获得推荐过的历史记录并分页
    :param request:
    :return:
    """
    validaters = [('uid', 0, int),
                  ('page_no', 10, int),
                  ('page_size', 1, int)]
    uid, page_no, page_size = type_cast_request_args(request, validaters)
    if any([x is None for x in (uid, page_no, page_size)]):
        j = {'status': -1, 'msg': '参数传递非法', 'data': []}
        logger.error(j)
        return JsonResponse(j, safe=False)
    begin = page_size * (page_no - 1)
    end = begin + page_size
    history = mongo_models.JianHistory.get_jian_history(uid, begin, end)
    logger.info(f'{uid} 获取推荐历史 history= {history}')
    j = {'status': 0, 'data': history}
    return JsonResponse(j, safe=True)
