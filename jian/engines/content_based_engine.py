#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import json
import logging
import os
from functools import lru_cache
from typing import List, Tuple
from datetime import datetime

import jieba

from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override
from jian import mongo_models

logger = logging.getLogger(__name__)
pwd = os.path.dirname(os.path.abspath(__name__))
userdict = os.path.join(pwd, 'userdict.txt')
jieba.load_userdict(userdict)


class ContentBasedEngine(BaseEngine):
    name = "基于内容的推荐引擎"

    def __init__(self, process, task_count):
        super(ContentBasedEngine, self).__init__(process, task_count)

    @override
    def core_algo(self):
        """
        使用结巴分词和基于TD-IDF算法，计算内容相似度，进行推荐。算法离线算好,直接取出.
        :return:
        """
        if self.process.len_tracked == 0:
            return []
        d = {}
        for cid in self.process.tracked_cids:
            # 内容最相似的已经离线计算好,存到了redis里面,直接取出来.
            cid_simi_list = mongo_models.ContentSimilarityOffline.get_cached_similarity_by_cid(cid)
            if len(cid_simi_list) == 0:
                continue
            for cid, simi in cid_simi_list:
                d.setdefault(cid, [0, 0.0])  # [sim的累加,次数]
                d[cid][0] += simi
                d[cid][1] += 1
        logger.info('相似度计算后')
        # 过滤

        # 经过日志发现,摊平特别浪费时间,随着用户喜欢的增加,要摊平的result长度飙升.比如我的result长度现在是2千万多.所以考虑将计算过的d
        # 缓存起来.
        # 具体方案: 将key为uid,值为len(tracked_ids),len(simi_per_cid),d缓存起来.当len(tracked_ids),len(simi_per_cid)变大时,
        # 将d取出,在d基础上做更新,更新的内容是作为条件计算.这样只需要计算没算过的那部分result就可以了.
        # d = cached_d + (len_simi_now - len_simi_cache) * len_tracked_cached +
        # (len_tracked_now - len_tracked_cached) * len_simi_now
        logger.info('摊平后')
        for f_id in self.process.fitering_cids:
            d.pop(f_id, None)
        logger.info('过滤后')
        result = []
        for cid, sumsim_count_list in d.items():
            result.append([cid, sumsim_count_list[0] / sumsim_count_list[1]])
        logger.info('计算加权平均后')
        # 排序
        result: List[List[int, float]] = sorted(result,
                                                key=lambda cid_sim_tuple: cid_sim_tuple[1],
                                                reverse=True)[:self.task_count]
        logger.info('排序后')
        for r in result:
            r.append(self.__class__.__name__)
        return result
