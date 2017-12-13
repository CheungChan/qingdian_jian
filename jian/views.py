import logging
from collections import Counter
from datetime import datetime
from random import shuffle
from django.http import JsonResponse

from jian import models
from qingdian_jian.utils import get_mongo_collection

TRACK_COLLECTION_NAME = 'jian_track'
TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'
logger = logging.getLogger(__name__)


def track(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    try:
        uid = int(uid)
        cid = int(cid)
    except ValueError:
        j = {'status': -1, 'msg': 'param error'}
        return JsonResponse(j, safe=True)
    tags = models.ContentsTag.get_tids_by_cid(cid)
    db = get_mongo_collection(TRACK_COLLECTION_NAME)
    data = {'uid': uid, 'cid': cid, 'tids': tags, 'update_time': datetime.now()}
    db.insert_one(data)
    logger.info(f'track data={data}')
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)


def track_diss(request):
    uid = request.GET.get('uid')
    cid = request.GET.get('cid')
    try:
        uid = int(uid)
        cid = int(cid)
    except ValueError:
        j = {'status': -1, 'msg': 'param error'}
        return JsonResponse(j, safe=True)
    tags = models.ContentsTag.get_tids_by_cid(cid)
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    data = {'uid': uid, 'cid': cid, 'tids': tags, 'update_time': datetime.now()}
    db.insert_one(data)
    logger.info(f'track_diss data={data}')
    j = {'status': 0, 'msg': 'ok'}
    return JsonResponse(j, safe=False)


def diss_list(request):
    uid = request.GET.get('uid')
    try:
        uid = int(uid)
    except ValueError:
        j = {'status': -1, 'msg': 'param error'}
        return JsonResponse(j, safe=True)
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    records = []
    for r in db.find({'uid': uid}):
        records.append(r['cid'])
    records = list(set(records))
    j = {'status': 0, 'data': records}
    logger.info(f'diss_list j={j}')
    return JsonResponse(j, safe=False)


def uids_by_uid(request):
    uid = request.GET.get('uid')
    n = request.GET.get('n', 20)
    try:
        uid = int(uid)
        n = int(n)
    except ValueError:
        j = {'status': -1, 'msg': 'param error'}
        return JsonResponse(j, safe=True)

    # 找到此用户的浏览记录
    db = get_mongo_collection(TRACK_COLLECTION_NAME)
    tracked = []
    for t in db.find({'uid': uid}):
        tracked.append(t)
    len_tracked = len(tracked)
    logger.info(f'uid {uid} 找到tids个数 {len_tracked}')
    if len_tracked == 0:
        jian_cids = []
    else:

        # 所有此用户浏览过的cid
        tracked_cids = list(set([t['cid'] for t in tracked]))
        # 如 [166, 105, 234, 187, 188]

        # 所有浏览记录里面的tid和要出现几个cid
        tracked_tids = []
        for t in tracked:
            tracked_tids += t['tids']
        c = Counter(tracked_tids)
        most_common = c.most_common()
        logger.info(f'most_common {most_common}')
        # 如 [(1, 16), (2, 14), (7, 14), (8, 14), (11, 14), (13, 5), (4, 2), (9, 2)]
        s = sum(c.values())  # 总的标签个数
        tid_roundnum = [[t[0], round(t[1] / s * n)] for t in most_common]
        # 需要某标签的个数 = 某标签浏览的次数 / 所有标签浏览次数 * 需要的个数
        logger.info(f'tid_roundnum= {tid_roundnum}')
        # 如 tid_num= [[1, 4], [2, 3], [7, 3], [8, 3], [11, 3], [13, 1], [4, 0], [9, 0]]

        # 取正好要的n个 由于most_common元素的第1（从0开始）个元素是四舍五入的结果，如果加起来的和大于n，跳过，最后再处理，
        # 如果加起来小于n，则加在第0个（从0开始）上面。
        num = 0
        tid_num = []
        for t in tid_roundnum:
            tid_num.append(t)
            num += t[1]  # 统计有了多少个标签了
            if num > n:
                break
        else:
            logger.info(f'四舍五入少了，加上{n-num}')
            tid_num[0][1] += n - num
        logger.info(f'tid_num= {tid_num}')
        # 获得数据库中tid对应的所有cids
        jian_cids = []
        for tid, limit in tid_num:
            if limit == 0:
                continue
            cids = models.ContentsTag.get_limit_cids(tid, None, limit)
            jian_cids += cids
        jian_cids = list(set(jian_cids))[:n]
    len_jian = len(jian_cids)
    logger.info(f'获得推荐{len_jian}个')
    len_lack = n - len_jian
    if len_lack > 0:
        jian_cids += models.ContentsTag.get_limit_cids(None, None, len_lack)
        logger.info(f'不够，从新鲜中获取{len_lack}个')
    shuffle(jian_cids)
    j = {'status': 0, 'data': jian_cids}
    logger.info(f'jian j= {j}')
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
