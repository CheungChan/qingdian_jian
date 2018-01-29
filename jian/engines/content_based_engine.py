#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import json
import logging
import os
from functools import lru_cache
from math import sqrt
from typing import List, Tuple

import jieba
from werkzeug.utils import cached_property
from jian import models
from jian.engines.base_engine import BaseEngine
from qingdian_jian.settings import CACHE_SECONDS
from qingdian_jian.utils import override, use_cache

logger = logging.getLogger(__name__)
pwd = os.path.dirname(os.path.abspath(__name__))
userdict = os.path.join(pwd, 'userdict.txt')
jieba.load_userdict(userdict)
import jieba.analyse


class ContentBasedEngine(BaseEngine):
    name = "基于内容的推荐引擎"

    def __init__(self, process, task_count):
        super(ContentBasedEngine, self).__init__(process, task_count)

    @override
    def core_algo(self):
        """
        使用结巴分词和基于TD-IDF算法，计算内容相似度，进行推荐。
        :return:
        """
        if self.process.len_tracked == 0:
            return []
        result: List[Tuple[int, float, str]] = []
        tracked_id_str = {}

        for cid in self.process.tracked_cids:
            d = {k: v for k, v in self.all_content_idstr_dict.items() if k == cid}
            if not d:
                continue
            else:
                tracked_id_str[cid] = d.get(cid, '')
        all_id_str = {k: v for k, v in self.all_content_idstr_dict.items() if k not in self.process.fitering_cids}
        for id1, str1 in tracked_id_str.items():
            for id2, str2 in all_id_str.items():
                sim = self.str_similarity(id1, str1, id2, str2)
                if 0.0 < sim < 9.9:
                    result.append((id2, sim, self.__class__.__name__))
        result = sorted(result,
                        key=lambda cid_sim_engine_tuple: cid_sim_engine_tuple[1],
                        reverse=True)[:self.task_count]
        return result

    # @classmethod
    # @lru_cache(None)
    # def ignore_str(cls, s: str) -> str:
    #     """
    #     去除字符串中的非人类语言
    #     :param s:
    #     :return:
    #     """
    #     IGNORE_MATCH = re.compile('^\S+：|@\S+\s|cn：|服装：|con：')
    #     # 用户昵称|@xxx|cn:|服装:|con:
    #     at = IGNORE_MATCH.findall(s)
    #     # logger.info(f'去除非人类语言，发现了匹配 {at}')
    #     for a in at:
    #         s = s.replace(a, '')
    #     return s

    # @classmethod
    # @lru_cache(None)
    # def no_stop_flag_str(cls, s: str, stop_flag=None) -> list:
    #     """
    #     去除特定词性
    #     :param s:
    #     :param stop_flag 要去除的词性列表
    #     :return:
    #     """
    #     if not stop_flag:
    #         stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']
    #     words = pseg.cut(s)
    #     result = []
    #     for word, flag in words:
    #         if flag not in stop_flag:
    #             result.append(word)
    #     return result

    @classmethod
    @lru_cache(None)
    def tf_idf_str(cls, s, topK=20, withWeight=True, ignore=True) -> list:
        """
        使用TF-IDF算法，去除关键词
        :param s:
        :param topK:
        :param withWeight: 返回值是否带关键词的权重
        :return:
        """
        # if ignore:
        #     s = cls.ignore_str(s)
        a = jieba.analyse.extract_tags(s, withWeight=withWeight, topK=topK)
        # logger.debug(a)
        return a

    @classmethod
    def merge_tag(cls, tag1=None, tag2=None):
        v1 = []
        v2 = []
        tag_dict1 = {i[0]: i[1] for i in tag1}
        tag_dict2 = {i[0]: i[1] for i in tag2}
        merged_tag = set(list(tag_dict1.keys()) + list(tag_dict2.keys()))
        for i in merged_tag:
            if i in tag_dict1:
                v1.append(tag_dict1[i])
            else:
                v1.append(0)

            if i in tag_dict2:
                v2.append(tag_dict2[i])
            else:
                v2.append(0)
        return v1, v2

    @classmethod
    def dot_product(cls, v1, v2):
        """
        计算矩阵的点积
        :param v1:
        :param v2:
        :return:
        """
        return sum(a * b for a, b in zip(v1, v2))

    @classmethod
    def magnitude(cls, vector):
        return sqrt(cls.dot_product(vector, vector))

    @classmethod
    def similarity(cls, f1: list, f2: list) -> float:
        """
        计算余弦相似度
        :param f1: 以(关键词,词频)为元素的列表1
        :param f2: 以(关键词,词频)为元素的列表2
        :return:
        """
        return cls.dot_product(f1, f2) / (
                cls.magnitude(f1) * cls.magnitude(f2) + 0.00000001)

    @classmethod
    @lru_cache(None)
    def str_similarity(cls, id1: int, s1: str, id2: int, s2: str) -> float:
        """
        求解两个字符串的相似度
        :param s1: 字符串1
        :param s2: 字符串2
        :return:
        """
        if id2 < id1:
            id1, id2 = id2, id1
            s1, s2 = s2, s1
        name = f"azhang_jian_contentsim_{id1}_{id2}"

        def value_func():
            tag1 = cls.tf_idf_str(s1)
            tag2 = cls.tf_idf_str(s2)
            v1, v2 = cls.merge_tag(tag1, tag2)
            return cls.similarity(v1, v2)

        retrive_value_func = lambda val: float(val)
        return use_cache(name, value_func, retrive_value_func, cache_seconds=None)

    @cached_property
    def all_content_idstr_dict(self):
        name = "azhang_jian_allcontentidstr"
        value_func = lambda: json.dumps(models.Contents.get_contentstr_list())
        retrive_value_func = lambda val: {int(k): v for k, v in json.loads(val).items()}
        return use_cache(name, value_func, retrive_value_func, cache_seconds=CACHE_SECONDS)
