#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

from logzero import logger
from typing import List, Tuple
from abc import abstractmethod, ABCMeta

from werkzeug.utils import cached_property

from jian.utils import get_trackcids_tracktids, get_track_disscids_diss_tids, get_jian_history


class BaseEngine(metaclass=ABCMeta):
    """
    所有推荐引擎的基类
    引擎是一个callable，调用获得推荐结果。
    """

    @cached_property
    def tracked_cids(self):
        """
        :return: 所有被追踪（喜欢）的内容id
        """
        return get_trackcids_tracktids(self.uid)[0]

    @cached_property
    def tracked_tids(self):
        """
        :return: 所有被追踪（❤️）的标签id
        """
        return get_trackcids_tracktids(self.uid)[1]

    @cached_property
    def dissed_cids(self):
        """
        :return: 所有不❤️的内容id
        """
        return get_track_disscids_diss_tids(self.uid)[0]

    @cached_property
    def dissed_tids(self):
        """
        :return: 所有不❤️的标签id
        """
        return get_track_disscids_diss_tids(self.uid)[1]

    @cached_property
    def jianed_cids(self):
        """
        :return: 所有已推荐过的内容id
        """
        return get_jian_history(self.uid)

    def __init__(self, uid, n):
        """
        :param uid: 用户id
        :param n: 要获得推荐的个数
        :param len_jian 推荐算法得到的个数
        :param len_rand 随机得到的个数
        """
        self.uid = uid
        self.n = n
        self.prepare_signature_vector()

    def prepare_signature_vector(self):
        """
        生成用户特征向量
        :return:
        """
        self.len_tracked = len(self.tracked_tids)
        logger.debug(f'uid {self.uid} 找到tids个数 {self.len_tracked}')

    @abstractmethod
    def core_algo(self) -> List[Tuple[int, float, str]]:
        """
        算法核心抽象方法
        :return:
        """
        pass

    def process_recommend(self):
        """
        推荐内容
        :return:
        """
        result: List[Tuple[int, float, str]] = []
        if self.len_tracked == 0:
            pass
        else:
            result = self.core_algo()
        return result

    def __call__(self, *args, **kwargs):
        # 引擎是一个callable，调用获得推荐结果。
        return self.process_recommend()
