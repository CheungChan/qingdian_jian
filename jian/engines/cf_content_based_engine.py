#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/3/9
# @Author  : 陈章

import logging
from math import sqrt
from typing import Dict, List, Tuple
from tqdm import tqdm
from jian import models, mongo_models
from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override

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
        content_user_grade = self.get_content_user_grade()
        logger.info('')
        content_similarity = self.calculate_content_similarity(content_user_grade)
        logger.info('')
        result = self.get_recommendations(content_user_grade, content_similarity)
        logger.info(result)
        return result

    @staticmethod
    def get_content_user_grade() -> Dict[int, Dict[int, int]]:
        """
        得到内容 用户 评分的字典
        :return:
        """
        all_cids = models.Contents.get_all_normal_cids()
        all_uids = models.User.get_all_userids()
        content_user_grade = {cid: {uid: 0 for uid in all_uids} for cid in all_cids}
        for uid in all_uids:
            tracked_cids, _ = mongo_models.JianTrack.get_trackcids_tracktids(uid)
            dissed_cids, _ = mongo_models.JianTrackDiss.get_track_disscids_diss_tids(uid)
            for cid in tracked_cids:
                if cid in content_user_grade and uid in content_user_grade[cid]:
                    content_user_grade[cid][uid] += 1
            for cid in dissed_cids:
                if cid in content_user_grade and uid in content_user_grade[cid]:
                    content_user_grade[cid][uid] -= 1
        return content_user_grade

    @staticmethod
    def sim_distance(content_user_grade: Dict[int, Dict[int, int]], content1: int, content2: int) -> float:
        # 得到一个share items 的列表
        si = {}
        for content in content_user_grade[content1]:
            if content in content_user_grade[content2]:
                si[content] = 1
        # 如果两者没有共同之处,则返回0
        if len(si) == 0: return 0
        # 计算所有差值的平方和
        sum_of_squares = sum(pow(content_user_grade[content1][user] - content_user_grade[content2][user], 2) for user in
                             content_user_grade[content1] if user in content_user_grade[content2])
        return 1 / (1 + sqrt(sum_of_squares))

    def top_matches(self, content_user_grade: Dict[int, Dict[int, int]], content: int) -> List[Tuple[float, int]]:
        """
        从字典中返回最为匹配者.
        返回结果的个数均为可选参数
        :param content_user_grade:
        :param content:
        :param n:
        :param similarity:
        :return:
        """
        scores = [(self.sim_distance(content_user_grade, content, other), other) for other in
                  content_user_grade
                  if
                  other != content]
        # 对列表进行排序,评价值最高者排在最前面
        scores.sort()
        scores.reverse()
        return scores[0:self.task_count]

    def calculate_content_similarity(self, content_user_grade: Dict[int, Dict[int, int]]) \
            -> Dict[int, List[Tuple[float, int]]]:
        # 建立字典,以给出与整合写物品最为相近的所有其他物品
        content_similarity = {}
        c = 0
        for content in tqdm(content_user_grade, desc='calculate_content_similarity'):
            c += 1
            if c % 100 == 0: print(f'{c} / {len(content_user_grade)}')
            # 针对大数据集更新状态变量
            scores = self.top_matches(content_user_grade, content)
            content_similarity[content] = scores
        return content_similarity

    def get_recommendations(self, content_user_grade: Dict[int, Dict[int, int]],
                            content_similarity: Dict[int, List[Tuple[float, int]]]):
        user_ratings = content_user_grade[self.process.uid]
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

        # 将每个合计值除以加权和,求出平均值
        rankings = [(score / total_sim[content], content) for content, score in scores.items()]

        # 按照最高值到最低值排序,返回评分结果
        rankings.sort()
        rankings.reverse()
        return rankings
