import logging
from datetime import datetime

from django.http import JsonResponse

from jian import models
from qingdian_jian.utils import get_mongo_collection, trans_int

TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'
logger = logging.getLogger(__name__)


def track_diss(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    uid, cid = trans_int(uid, cid)
    if uid is None or cid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    tags = models.ContentsTag.get_tids_by_cid(cid)
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    data = {'uid': uid, 'cid': cid, 'tids': tags, 'update_time': datetime.now()}
    db.insert_one(data)
    logger.info(f'track_diss data={data}')
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)


def diss_list(request):
    uid = request.GET.get('uid')
    uid = trans_int(uid)
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
