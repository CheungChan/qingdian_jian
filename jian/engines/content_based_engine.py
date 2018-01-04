from logzero import logger

from jian import models
from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override
import re
from functools import lru_cache
from math import sqrt
import os
import jieba
from typing import List

pwd = os.path.dirname(os.path.abspath(__name__))
userdict = os.path.join(pwd, 'userdict.txt')
jieba.load_userdict(userdict)
import jieba.analyse
import jieba.posseg as pseg


class ContentBasedEngine(BaseEngine):
    """
    基于内容的推荐引擎
    """

    def __init__(self, uid, n):
        logger.debug('创建基于内容的引擎')
        super(ContentBasedEngine, self).__init__(uid, n)

    @override
    def core_algo(self):
        result: List[int, float, str] = []
        tracked_id_str = {}
        for cid in self.tracked_cids:
            d = models.Contents.get_contentstr_list(cid)
            if not d:
                continue
            else:
                tracked_id_str[cid] = d.get(cid, '')
        logger.debug(f'去掉不含描述的内容后 tracked_id_str={tracked_id_str}')
        all_id_str = models.Contents.get_contentstr_list()
        logger.debug(f'所有内容id和内容 all_id_str={all_id_str}')
        for id1, str1 in tracked_id_str.items():
            for id2, str2 in all_id_str.items():
                sim = self.str_similarity(str1, str2)
                if sim > 0.0:
                    result.append((id2, sim, self.__class__.__name__))
        logger.debug(f'result：{result}')
        return result

    @classmethod
    @lru_cache(None, typed=True)
    def ignore_str(cls, s: str) -> str:
        """
        去除字符串中的非人类语言
        :param s:
        :return:
        """
        IGNORE_MATCH = re.compile('^\S+：|@\S+\s|cn：|服装：|con：')
        # 用户昵称|@xxx|cn:|服装:|con:
        at = IGNORE_MATCH.findall(s)
        # logger.info(f'去除非人类语言，发现了匹配 {at}')
        for a in at:
            s = s.replace(a, '')
        return s

    @classmethod
    @lru_cache(None, typed=True)
    def no_stop_flag_str(cls, s: str, stop_flag=None) -> list:
        """
        去除特定词性
        :param s:
        :param stop_flag 要去除的词性列表
        :return:
        """
        if not stop_flag:
            stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']
        words = pseg.cut(s)
        result = []
        for word, flag in words:
            if flag not in stop_flag:
                result.append(word)
        return result

    @classmethod
    @lru_cache(None, typed=True)
    def tf_idf_str(cls, s, topK=20, withWeight=True, ignore=True) -> list:
        """
        使用TF-IDF算法，去除关键词
        :param s:
        :param topK:
        :param withWeight: 返回值是否带关键词的权重
        :return:
        """
        if ignore:
            s = cls.ignore_str(s)
        a = jieba.analyse.extract_tags(s, withWeight=withWeight, topK=topK)
        # logger.debug(a)
        return a

    @classmethod
    @lru_cache(None, typed=True)
    def text_rank_str(cls, s, topK=20, withWeight=True) -> list:
        """
        使用text_rank算法，其余同tf_idf_str
        :param s:
        :param topK:
        :param withWeight:
        :return:
        """
        a = jieba.analyse.textrank(s, withWeight=withWeight, topK=topK)
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
    @lru_cache(None, typed=True)
    def str_similarity(cls, s1: str, s2: str) -> float:
        """
        求解两个字符串的相似度
        :param s1: 字符串1
        :param s2: 字符串2
        :return:
        """
        tag1 = cls.tf_idf_str(s1)
        tag2 = cls.tf_idf_str(s2)
        v1, v2 = cls.merge_tag(tag1, tag2)
        return cls.similarity(v1, v2)
