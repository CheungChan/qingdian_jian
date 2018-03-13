#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import logging
from collections import Counter
from datetime import datetime, timedelta
from functools import lru_cache
from typing import List, Dict, Tuple, Union

import pymongo

from jian import models
from qingdian_jian.utils import get_mongo_collection, jsonKeys2str, jsonKeys2int

logger = logging.getLogger(__name__)


class JianTrack:
    collection_name = 'jian_track'

    # uid: xx cid: xx tids: [xx,yy] update_time: xx

    @classmethod
    def get_trackcids_tracktids(cls, uid: int):
        """
        获取track（喜欢）过的内容id和标签id
        :param uid:
        :return:
        """
        db = get_mongo_collection(cls.collection_name)
        trackcids = []
        tracktids = []
        for t in db.find({'uid': uid}).sort('update_time', pymongo.DESCENDING):
            trackcids.append(t['cid'])
            tracktids += t['tids']
        # logger.debug(f'len_trackcid= {len(trackcids)}, len_tracktid= {len(tracktids)}')
        return trackcids, tracktids

    @classmethod
    def get_recently_hot_tracked(cls, recent_days: int = 7, limit: int = 20, nocids: List[int] = None):
        """
        获取最近热门的track。
        :param recent_days:
        :param limit:
        :param nocids: 要排除的内容id
        :return:
        """
        recent = datetime.now() - timedelta(days=recent_days)
        if nocids is None:
            nocids = []
        db = get_mongo_collection(cls.collection_name)
        recent_tracked_cids = []
        curor = db.find({'update_time': {'$gte': recent}, 'cid': {'$nin': nocids}}).sort('update_time',
                                                                                         pymongo.DESCENDING)
        for t in curor:
            recent_tracked_cids.append(t['cid'])
        c = Counter(recent_tracked_cids)
        most_common = c.most_common(limit)
        sum_most_common = sum([i[1] for i in most_common])
        cid_sim_list = [(m[0], m[1] / sum_most_common) for m in most_common]
        return cid_sim_list

    @classmethod
    def store_track_cid(cls, uid: int, cid: int, client: int, behavior: int, device_id: str, from_jian: int):
        """
        保存埋点结果cid
        """
        tags = models.ContentsTag.get_tids_by_cid(cid)
        db = get_mongo_collection(cls.collection_name)
        data = {'uid': uid, 'cid': cid, 'tids': tags, 'update_time': datetime.now(), 'client': client,
                'device_id': device_id, 'behavior': behavior, 'from_jian': from_jian}
        db.insert_one(data)
        logger.info(f'track data={data}')

    @classmethod
    def statistics_rencent_tracked_docs(cls, from_datetime: datetime, end_datetime: datetime, client: int = None):
        """
        统计一定时间范围内的喜欢的内容id
        :param from_datetime:
        :param end_datetime:
        :param client
        :return:
        """
        db = get_mongo_collection(cls.collection_name)
        if from_datetime and end_datetime:
            condition = {'from_jian': 1, 'update_time': {'$gte': from_datetime, '$lte': end_datetime}}
        else:
            condition = {'from_jian': 1}
        if client is not None:
            condition.update({'client': client})
        return list(db.find(condition).sort('update_time', pymongo.DESCENDING))


class JianTrackDiss:
    collection_name = 'jian_track_diss'

    # uid:xx cid:xx tids:[xx,yy]

    @classmethod
    def get_track_disscids_diss_tids(cls, uid: int):
        """
        获取不喜欢的内容id和标签id,不去重。如果要去重，请处理返回值。
        :param uid:
        :return:
        """
        db = get_mongo_collection(cls.collection_name)
        diss_cids = []
        diss_tids = []
        for d in db.find({'uid': uid}).sort('update_time', pymongo.DESCENDING):
            cid = d.get('cid')
            if cid:
                diss_cids.append(cid)
            diss_tids += d['tids']
        # logger.debug(f'获取不喜欢记录len_diss_cids={len(diss_cids)}, len_diss_tids={len(diss_tids)}')
        return diss_cids, diss_tids

    @classmethod
    def store_diss_cid(cls, uid: int, cid: int, client: int, device_id: str):
        """
        保存不喜欢的内容id
        """
        data = {'uid': uid, 'cid': cid, 'client': client, 'device_id': device_id}
        db = get_mongo_collection(cls.collection_name)
        if db.count(data) == 0:
            tags = models.ContentsTag.get_tids_by_cid(cid)
            data.update({'tids': tags, 'update_time': datetime.now()})
            db.insert_one(data)
            logger.info(f'插入，track_diss data={data}')
        else:
            logger.error(f'已存在， track_diss data={data}')

    @classmethod
    def store_diss_tid(cls, uid: int, tid: int, client: int, device_id: int):
        """
        保存不喜欢的标签id
        """
        db = get_mongo_collection(cls.collection_name)
        data = {'uid': uid, 'tids': [tid, ], 'client': client, 'device_id': device_id}
        if db.count(data) == 0:
            data.update({'update_time': datetime.now()})
            db.insert_one(data)
            logger.info(f'插入，track_diss_theme data={data}')
        else:
            logger.error(f'已存在， track_diss_theme data={data}')

    @classmethod
    def statistics_rencent_dissed_docs(cls, from_datetime: datetime, end_datetime: datetime, client: int):
        """
        统计一定时间范围内的不喜欢的内容id
        :param from_datetime:
        :param end_datetime:
        :return:
        """
        db = get_mongo_collection(cls.collection_name)
        if from_datetime and end_datetime:
            condition = {'update_time': {'$gte': from_datetime, '$lte': end_datetime}}
        else:
            condition = {}
        if client is not None:
            condition.update({'client': client})
        return list(db.find(condition).sort('update_time', pymongo.DESCENDING))


class JianHistory:
    collection_name = 'jian_history'

    # uid:xx jian_cids:xx analyze:xx

    @classmethod
    def store_tuijian_history(cls, uid: int, jian_cids: List[int], analyze: Dict):
        """
        将推荐过的存储记录，下次不再推荐推荐过的
        :param uid:
        :param jian_cids:
        :return:
        """
        if len(jian_cids) == 0:
            return
        data = {'uid': uid, 'jids': jian_cids, 'analyze': analyze, 'update_time': datetime.now()}
        db = get_mongo_collection(cls.collection_name)
        db.insert_one(data)

    @classmethod
    def get_jian_history(cls, uid: int, begin: int = None, end: int = None):
        """
        获取推荐历史
        :param uid:
        :param begin:
        :param end:
        :return:
        """
        db = get_mongo_collection(cls.collection_name)
        history = []
        hs = db.find({'uid': uid}).sort('update_time', pymongo.DESCENDING)
        for h in hs:
            history += h['jids']
        if begin is not None and end is not None:
            history = history[begin:end]
        logger.debug(f'获取到推荐过的历史长度 {len(history)}')
        return history

    @classmethod
    def statistics_rencent_jianed_docs(cls, from_datetime: datetime, end_datetime: datetime, client: int = None):
        """
        统计一定时间范围内的推荐历史
        :param from_datetime:
        :param end_datetime:
        :return:
        """
        db = get_mongo_collection(cls.collection_name)
        if from_datetime and end_datetime:
            condition = {'update_time': {'$gte': from_datetime, '$lte': end_datetime}}
        else:
            condition = {}
        if client is not None:
            condition.update({'analyze.client': client})
        return list(db.find(condition).sort('update_time', pymongo.DESCENDING))


class SimilarityOfContent:
    collection_name = 'similarity_of_content'

    # cid:xxx cid2_sim:[[1,0.1],[2,0.3],..]
    @classmethod
    @lru_cache(None)
    def get_cached_similarity_by_cid(cls, cid) -> Tuple[List[Union[int, float]], int]:
        db = get_mongo_collection(cls.collection_name)
        cached_value = db.find_one({'cid': cid})
        if cached_value:
            return cached_value['cid2_sim'], cached_value['cached_max_cid']
        else:
            return [], 0


class UserContentSimilarityCache:
    collection_name = 'user_content_similarity_cache'

    @classmethod
    def set_cached_user_content_similarity(cls, uid: int,
                                           kcid_vcached_max_cid_dict: Dict[int, int],
                                           kcid_vtuplesumsimi0_countsimi1_dict: Dict[int, Tuple[float, int]]):
        """

        :param uid:
        @:param kcid_vcached_max_cid_dict : key为内容id,value为 内容id对应的相似内容的长度.由于每个内容相似内容的长度不一定相同,可能
        正在计算中,导致后面的内容相似内容长度短于开始的.
        :param kcid_vtuplesumsimi0_countsimi1_dict: key为内容id,value为相似度的和相似度出现的次数的tuple组成的dict .
        :return:
        """
        db = get_mongo_collection(cls.collection_name)
        data = {'uid': uid,
                'kcid_vcached_max_cid_dict': jsonKeys2str(kcid_vcached_max_cid_dict),
                'kcid_vtuplesumsimi0_countsimi1_dict': jsonKeys2str(kcid_vtuplesumsimi0_countsimi1_dict),
                'update_time': datetime.now()}
        db.update({'uid': uid}, data, upsert=True)

    @classmethod
    def get_cached_user_content_similarity(cls, uid) -> Tuple[Dict[int, int], Dict[int, Tuple[float, int]]]:
        """

        :param uid:
        :return: kcid_vcached_max_cid_dict和kcid_vtuplesumsimi0_countsimi1_dict组成的tuple,两个变量解释见
        cls.set_cached_user_content_similarity
        """
        db = get_mongo_collection(cls.collection_name)
        cached_value = db.find_one({'uid': uid})
        if cached_value:
            return jsonKeys2int(cached_value['kcid_vcached_max_cid_dict']), jsonKeys2int(
                cached_value['kcid_vtuplesumsimi0_countsimi1_dict'])
        else:
            return {}, {}
