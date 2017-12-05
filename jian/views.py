from django.http import JsonResponse
from jian import models
from qingdian_jian.utils import get_mongo_collection
from datetime import datetime

COLLECTION_NAME = 'jian_track'


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
    tags = models.ContentsTag.objects.filter(content__pk=cid).values('tag_id')
    tags = [t['tag_id'] for t in tags]
    db = get_mongo_collection(COLLECTION_NAME)
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
