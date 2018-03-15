#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/3/9
# @Author  : 陈章

import logging
from typing import Dict, List, Tuple

from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override
from jian import mongo_models

logger = logging.getLogger(__name__)


class CFContentBasedEngine(BaseEngine):
    name = '协同过滤基于内容的推荐引擎'

    def __init__(self, process, task_count):
        super(CFContentBasedEngine, self).__init__(process, task_count)

    @override
    def core_algo(self):
        """
        基于协同过滤进行推荐
        :return:
        """
        user_content_grade = mongo_models.CollaborativeFiltering.get_user_content_grade()
        content_similarity = mongo_models.CollaborativeFiltering.get_content_similarity()
        result = self.get_recommendations(user_content_grade, content_similarity)
        return result

    def get_recommendations(self, user_content_grade: Dict[int, Dict[int, int]],
                            content_similarity: Dict[int, List[Tuple[float, int]]]):
        user_ratings = user_content_grade.get(self.process.uid, {})
        logger.debug(f'len(user_rating)={len(user_ratings)})')
        scores = {}
        total_sim = {}

        # 循环遍历由当前用户评分的商品
        for content, rating in user_ratings.items():

            # 循环遍历与当前物品相近的物品
            for similarity, content2 in content_similarity[content]:

                # 如果用户已经对当前商品做过评价,则将其忽略
                if content2 in user_ratings: continue

                # 评价值与相似度加权之和
                scores.setdefault(content2, 0)
                scores[content2] += similarity * rating

                # 全部相似度之和
                total_sim.setdefault(content2, 0)
                total_sim[content2] += similarity
        # 过滤
        for cid in self.process.fitering_cids:
            scores.pop(cid, None)
        # 排序
        # 将每个合计值除以加权和,求出平均值
        result = [[content, score / total_sim[content]] for content, score in scores.items()]

        # 按照最高值到最低值排序,返回评分结果
        result: List[List[int, float]] = sorted(result,
                                                key=lambda cid_sim_tuple: cid_sim_tuple[1],
                                                reverse=True)[:self.task_count]
        for r in result:
            r.append(self.__class__.__name__)
        return result
