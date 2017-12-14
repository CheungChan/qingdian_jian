import logging

from django.http import JsonResponse

from jian.views.tuijian_algo import algo_jian_by_tag
from jian.views.tuijian_util import store_tuijian_history
from qingdian_jian.utils import trans_int

TRACK_COLLECTION_NAME = 'jian_track'
TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'
logger = logging.getLogger(__name__)


def uids_by_uid(request):
    uid = trans_int(request.GET.get('uid'))
    if uid is None:
        j = {'status': -1, 'data': []}
    else:
        j = {'status': 0, 'data': []}
    return JsonResponse(j, safe=False)


def cids_by_uid(request):
    uid = request.GET.get('uid')
    n = request.GET.get('n', 20)
    uid, n = trans_int(uid, n)
    if uid is None or n is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    jian = algo_jian_by_tag(uid, n)
    jian_cids = jian['jian_cids']
    jian_num = jian['jian_num']
    new_num = jian['new_num']
    store_tuijian_history(uid, jian_cids)
    j = {'status': 0, 'data': jian_cids, 'jian_num': jian_num, 'new_num': new_num}
    logger.info(f'jian j= {j}')
    return JsonResponse(j, safe=False)


def uids_by_cid(request):
    cid = request.GET.get('cid')
    j = {'status': 0, 'data': []}
    return JsonResponse(j, safe=False)


def cids_by_cid(request):
    cid = request.GET.get('cid')
    j = {'status': 0, 'data': []}
    return JsonResponse(j, safe=False)
