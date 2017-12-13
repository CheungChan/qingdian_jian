import logging
from datetime import datetime

from django.http import JsonResponse

from jian import models
from qingdian_jian.utils import get_mongo_collection, trans_int

TRACK_COLLECTION_NAME = 'jian_track'
logger = logging.getLogger(__name__)


def track(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    uid, cid = trans_int(uid, cid)
    if uid is None or cid is None:
        j = {'status': -1, 'data': []}
        return JsonResponse(j, safe=False)
    tags = models.ContentsTag.get_tids_by_cid(cid)
    db = get_mongo_collection(TRACK_COLLECTION_NAME)
    data = {'uid': uid, 'cid': cid, 'tids': tags, 'update_time': datetime.now()}
    db.insert_one(data)
    logger.info(f'track data={data}')
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)
