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


class CFUserBasedEngine(BaseEngine):
    name = '协同过滤基于用户的推荐引擎'

    def __init__(self, process, task_count):
        super(CFUserBasedEngine, self).__init__(process, task_count)

    @override
    def core_algo(self):
        """
        基于协同过滤进行推荐
        :return:
        """
        user_content_grade = self.get_user_content_grade()
        result = self.get_recommendations(user_content_grade, self.process.uid)
        print(result)
        result = []
        return result

    @staticmethod
    def get_user_content_grade() -> Dict[int, Dict[int, int]]:
        """
        得到用户 内容 评分的字典
        :return:
        """
        all_cids = models.Contents.get_all_normal_cids()
        all_uids = models.User.get_all_userids()
        user_content_grade = {uid: {cid: 0 for cid in all_cids} for uid in all_uids}
        for uid in all_uids:
            tracked_cids, _ = mongo_models.JianTrack.get_trackcids_tracktids(uid)
            dissed_cids, _ = mongo_models.JianTrackDiss.get_track_disscids_diss_tids(uid)
            for cid in tracked_cids:
                if uid in user_content_grade and cid in user_content_grade[uid]:
                    user_content_grade[uid][cid] += 1
            for cid in dissed_cids:
                if uid in user_content_grade and cid in user_content_grade[uid]:
                    user_content_grade[uid][cid] -= 1
        return user_content_grade

    @staticmethod
    def sim_distance(user_content_grade: Dict[int, Dict[int, int]], user1: int, user2: int) -> float:
        # 得到一个share items 的列表
        si = {}
        for item in user_content_grade[user1]:
            if item in user_content_grade[user2]:
                si[item] = 1
        # 如果两者没有共同之处,则返回0
        if len(si) == 0: return 0
        # 计算所有差值的平方和
        sum_of_squares = sum(pow(user_content_grade[user1][item] - user_content_grade[user2][item], 2) for item in
                             user_content_grade[user1] if item in user_content_grade[user2])
        return 1 / (1 + sqrt(sum_of_squares))

    def top_matches(self, user_content_grade: Dict[int, Dict[int, int]], user: int) -> List[Tuple[float, int]]:
        """
        从字典中返回最为匹配者.
        返回结果的个数均为可选参数
        :param user_content_grade:
        :param user:
        :param n:
        :param similarity:
        :return:
        """
        scores = [(self.sim_distance(user_content_grade, user, other), other) for other in
                  user_content_grade
                  if
                  other != user]
        # 对列表进行排序,评价值最高者排在最前面
        scores.sort()
        scores.reverse()
        return scores[0:self.task_count]

    def get_recommendations(self, user_content_grade: Dict[int, Dict[int, int]], user: int) -> List[Tuple[float, int]]:
        """
        获得推荐
        :param user_content_grade:
        :param user:
        :return:
        """
        totals = {}
        simSums = {}
        for other in tqdm(user_content_grade):
            # 不要和自己比较
            if other == user:
                continue
            sim = self.sim_distance(user_content_grade, user, other)

            # 忽略评价值为0或小于0的情况
            if sim <= 0:
                continue
            for item in user_content_grade[user]:
                # 只对自己还未曾看过的影片进行评价
                if item not in user_content_grade[user] or user_content_grade[user][item] == 0:
                    # 相似度 * 评价值
                    totals.setdefault(item, 0)
                    totals[item] += user_content_grade[other][item] * sim
                    # 相似度之和
                    simSums.setdefault(item, 0)
                    simSums[item] += sim

        # 建立归一化的列表
        rankings = [(total / simSums[item], item) for item, total in totals.items()]

        # 返回经过排序的列表
        rankings.sort()
        rankings.reverse()
        return rankings[0: self.task_count]
