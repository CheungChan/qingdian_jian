from django.http import JsonResponse
from jian import models
from qingdian_jian.utils import get_mongo_collection
from datetime import datetime
from qingdian_jian.settings import DEBUG

# if DEBUG:
#     TRACK_COLLECTION_NAME = 'jian_track_test'
#     TRACK_DISS_COLLECTION_NAME = 'jian_track_diss_test'
# else:
TRACK_COLLECTION_NAME = 'jian_track'
TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'


def track(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    if not all([uid, cid]):
        j = {'status': -1, 'msg': 'param error'}
        return JsonResponse(j, safe=False)
    try:
        uid = int(uid)
        cid = int(cid)
    except ValueError:
        j = {'status': -2, 'msg': 'param type error'}
        return JsonResponse(j, safe=True)
    tags = models.ContentsTag.get_tags_by_content_pk(cid)
    db = get_mongo_collection(TRACK_COLLECTION_NAME)
    data = {'uid': uid, 'cid': cid, 'tids': tags, 'update_time': datetime.now()}
    db.insert_one(data)
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)


def track_diss(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    if not all([uid, cid]):
        j = {'status': -1, 'msg': 'param error'}
        return JsonResponse(j, safe=False)
    try:
        uid = int(uid)
        cid = int(cid)
    except ValueError:
        j = {'status': -2, 'msg': 'param type error'}
        return JsonResponse(j, safe=True)
    tags = models.ContentsTag.get_tags_by_content_pk(cid)
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    data = {'uid': uid, 'cid': cid, 'tids': tags, 'update_time': datetime.now()}
    db.insert_one(data)
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)


def uids_by_uid(request):
    uid = request.GET.get('uid')
    j = {'status': 0, 'data': []}
    return JsonResponse(j, safe=False)


def cids_by_uid(request):
    uid = request.GET.get('uid')
    j = {'status': 0, 'data': []}
    return JsonResponse(j, safe=False)


def uids_by_cid(request):
    cid = request.GET.get('cid')
    j = {'status': 0, 'data': []}
    return JsonResponse(j, safe=False)


def cids_by_cid(request):
    cid = request.GET.get('cid')
    j = {'status': 0, 'data': []}
    return JsonResponse(j, safe=False)
