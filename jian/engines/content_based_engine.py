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
from qingdian_jian.utils import override, cache_redis

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
        result: List[Tuple[int, float, str]] = []
        for cid in self.process.tracked_cids:
            # 内容最相似的已经离线计算好,存到了redis里面,直接取出来.
            cid_simi_list = self.get_cached_similarity(cid)
            if len(cid_simi_list) == 0:
                continue
            result.extend(cid_simi_list)
        logger.info(datetime.now())
        # 过滤
        d = {}
        for cid, simi in result:
            d.setdefault(cid, [0, 0])  # [sim的累加,次数]
            d[cid][0] += simi
            d[cid][1] += 1
        for f_id in self.process.fitering_cids:
            d.pop(f_id, None)
        result = []
        for cid, sumsim_count_list in d.items():
            result.append([cid, sumsim_count_list[0] / sumsim_count_list[1]])
        # 排序
        result = sorted(result,
                        key=lambda cid_sim_tuple: cid_sim_tuple[1],
                        reverse=True)[:self.task_count]
        for r in result:
            r.append(self.__class__.__name__)
        return result

    @classmethod
    @lru_cache(None)
    def get_cached_similarity(cls, cid):
        name = f'azhang_jian_simi_{cid}'
        cached_value = cache_redis(name, retrive_value_func=lambda val: [] if val is None else json.loads(val))
        return cached_value
