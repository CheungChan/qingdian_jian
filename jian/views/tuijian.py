#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging

from django.http import JsonResponse

from jian import mongo_models
from jian.process import Process
from qingdian_jian.utils import trans_int, log_views

logger = logging.getLogger(__name__)


@log_views
def cids_by_uid(request):
    """
    用户调用获得推荐
    :param request:
    :return:
    """
    uid = request.GET.get('uid')
    n = request.GET.get('n', 20)
    client = request.GET.get('client', '')
    device_id = request.GET.get('device_id')
    uid, n, client = trans_int(uid, n, client)
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
    uid = request.GET.get('uid')
    page_size = request.GET.get('page_size', 10)
    page_no = request.GET.get('page_no', 1)
    uid, page_size, page_no = trans_int(uid, page_size, page_no)
    if any([x is None for x in (uid, page_no, page_size)]):
        j = {'status': -1, 'msg': '参数传递非法', 'data': []}
        logger.error(j)
        return JsonResponse(j, safe=False)
    begin = page_size * (page_no - 1)
    end = begin + page_size + 1
    history = mongo_models.JianHistory.get_jian_history(uid, begin, end)
    logger.info(f'{uid} 获取推荐历史 history= {history}')
    j = {'status': 0, 'data': history}
    return JsonResponse(j, safe=True)
