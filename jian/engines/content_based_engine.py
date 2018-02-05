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

        # 加载上次的计算结果
        kcid_vcached_max_cid_dict, kcid_vtuplesumsimi0_countsimi1_dict = mongo_models.UserContentSimilarityCache. \
            get_cached_user_content_similarity(self.process.uid)
        tracked_cids = list(set(self.process.tracked_cids))
        for cid1 in tracked_cids:
            # 内容最相似的已经离线计算好,存到了mongo里面,直接取出来.
            cid_simi_list, cached_max_cid_now = mongo_models.SimilarityOfContent.get_cached_similarity_by_cid(cid1)
            if len(cid_simi_list) == 0:
                # cid1没有相似的内容.
                continue
            cached_max_cid_lasttime = kcid_vcached_max_cid_dict.get(cid1, 0)
            len_calculate = cached_max_cid_now - cached_max_cid_lasttime
            if len_calculate > 0:
                logger.info(f'需要计算{len_calculate}个')
            # 加载上次计算的cid对应的相似的个数只计算未算过的.
            cid_simi_list = [(cid2, simi) for (cid2, simi) in cid_simi_list if
                             cached_max_cid_lasttime < cid2 <= cached_max_cid_now]
            for cid2, simi in cid_simi_list:
                kcid_vtuplesumsimi0_countsimi1_dict.setdefault(cid2, [0.0, 0])  # [sim的累加,次数]
                kcid_vtuplesumsimi0_countsimi1_dict[cid2][0] += simi
                kcid_vtuplesumsimi0_countsimi1_dict[cid2][1] += 1
            # 更新cid对应的相似的个数
            kcid_vcached_max_cid_dict[cid1] = cached_max_cid_now
        # 存储计算结果
        mongo_models.UserContentSimilarityCache.set_cached_user_content_similarity(self.process.uid,
                                                                                   kcid_vcached_max_cid_dict,
                                                                                   kcid_vtuplesumsimi0_countsimi1_dict)

        # 过滤
        for f_id in self.process.fitering_cids:
            kcid_vtuplesumsimi0_countsimi1_dict.pop(f_id, None)
        result = []
        for cid, sumsim_count_list in kcid_vtuplesumsimi0_countsimi1_dict.items():
            result.append([cid, sumsim_count_list[0] / sumsim_count_list[1]])
        # 排序
        result: List[List[int, float]] = sorted(result,
                                                key=lambda cid_sim_tuple: cid_sim_tuple[1],
                                                reverse=True)[:self.task_count]
        for r in result:
            r.append(self.__class__.__name__)
        return result
