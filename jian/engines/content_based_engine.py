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
        kcid_vlensimi_dict, kcid_vtuplesumsimi0_countsimi1_dict = mongo_models.UserContentSimilarityCache.get_cached_user_content_similarity(
            self.process.uid)
        logger.info('加载完成')
        for cid in list(set(self.process.tracked_cids)):
            # 内容最相似的已经离线计算好,存到了mongo里面,直接取出来.
            cid_simi_list = mongo_models.ContentSimilarityOffline.get_cached_similarity_by_cid(cid)
            if len(cid_simi_list) == 0:
                continue
            logger.info(len(cid_simi_list))
            len_simi_lasttime = kcid_vlensimi_dict.get(cid, 0)
            logger.info(len_simi_lasttime)
            # 加载上次计算的cid对应的相似的个数,通过切片只计算未算过的.
            for cid, simi in cid_simi_list[len_simi_lasttime:]:
                kcid_vtuplesumsimi0_countsimi1_dict.setdefault(cid, [0.0, 0])  # [sim的累加,次数]
                kcid_vtuplesumsimi0_countsimi1_dict[cid][0] += simi
                kcid_vtuplesumsimi0_countsimi1_dict[cid][1] += 1
            # 更新cid对应的相似的个数
            logger.info(len(kcid_vtuplesumsimi0_countsimi1_dict))
            kcid_vlensimi_dict[cid] = len(cid_simi_list)
            logger.info(len(kcid_vlensimi_dict))
        logger.info('相似度转换为dict后')
        # 存储计算结果
        mongo_models.UserContentSimilarityCache.set_cached_user_content_similarity(self.process.uid, kcid_vlensimi_dict,
                                                                                   kcid_vtuplesumsimi0_countsimi1_dict)

        # 过滤
        for f_id in self.process.fitering_cids:
            kcid_vtuplesumsimi0_countsimi1_dict.pop(f_id, None)
        logger.info('过滤后')
        result = []
        for cid, sumsim_count_list in kcid_vtuplesumsimi0_countsimi1_dict.items():
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
