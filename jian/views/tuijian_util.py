import logging
from datetime import datetime

from qingdian_jian.utils import get_mongo_collection

TRACK_COLLECTION_NAME = 'jian_track'
TRACK_DISS_COLLECTION_NAME = 'jian_track_diss'
JIAN_HISTORY_COLLECTION_NAME = 'jian_history'
logger = logging.getLogger(__name__)


def store_tuijian_history(uid: int, jian_cids: list):
    """
    将推荐过的存储记录，下次不再推荐推荐过的
    :param uid:
    :param jian_cids:
    :return:
    """
    data = {'uid': uid, 'jids': jian_cids, 'update_time': datetime.now()}
    db = get_mongo_collection(JIAN_HISTORY_COLLECTION_NAME)
    db.insert_one(data)
    logger.info(f'存储推荐记录{data}')


def get_jian_history(uid: int, begin=None, end=None):
    db = get_mongo_collection(JIAN_HISTORY_COLLECTION_NAME)
    history = []
    hs = db.find({'uid': uid})
    for h in hs:
        history += h['jids']
    if begin is not None and end is not None:
        history = history[begin:end]
    logger.info(f'获取到推荐过的历史 {history}')
    return history


def get_trackcids_tracktids(uid: int):
    db = get_mongo_collection(TRACK_COLLECTION_NAME)
    trackcids = []
    tracktids = []
    for t in db.find({'uid': uid}):
        trackcids.append(t['cid'])
        tracktids += t['tids']
    logger.info(f'获取到埋点记录trackcids= {trackcids}, trackedtids= {tracktids}')
    return trackcids, tracktids


def get_track_disscids_diss_tids(uid: int):
    db = get_mongo_collection(TRACK_DISS_COLLECTION_NAME)
    diss_cids = []
    diss_tids = []
    for d in db.find({'uid': uid}):
        diss_cids.append(d['cid'])
        diss_tids += d['tids']
    logger.info(f'获取不喜欢记录diss_cids={diss_cids}, diss_tids={diss_tids}')
    return diss_cids, diss_tids
