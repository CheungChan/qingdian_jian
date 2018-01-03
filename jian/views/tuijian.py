import logging

from django.http import JsonResponse

from jian.process_recommand import ProcessRecommand
from jian.views.tuijian_util import store_tuijian_history, get_jian_history
from qingdian_jian.utils import trans_int

TRACK_COLLECTION_NAME = 'jian_track'
TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'
logger = logging.getLogger(__name__)


def cids_by_uid(request):
    uid = request.GET.get('uid')
    n = request.GET.get('n', 20)
    uid, n = trans_int(uid, n)
    logger.info(f'访问cids_by_uid?uid={uid}&n={n}')
    if uid is None or n is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    data = ProcessRecommand(uid, n)()
    j = {'status': 0, 'data': data}
    logger.info(f'jian j= {j}')
    return JsonResponse(j, safe=False)


def jian_history(request):
    uid = request.GET.get('uid')
    page_size = request.GET.get('page_size', 10)
    page_no = request.GET.get('page_no', 1)
    uid, page_size, page_no = trans_int(uid, page_size, page_no)
    logger.info(f'访问jian_history?uid={uid}&page_size={page_size}&page_no={page_no}')
    if page_size is None or page_no is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    begin = page_size * (page_no - 1)
    end = begin + page_size + 1
    history = get_jian_history(uid, begin, end)
    logger.info(f'{uid} 获取推荐历史 history= {history}')
    j = {'status': 0, 'data': history}
    return JsonResponse(j, safe=True)
