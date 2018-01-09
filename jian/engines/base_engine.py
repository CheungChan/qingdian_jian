#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging
from abc import abstractmethod, ABCMeta
from typing import List, Tuple

logger = logging.getLogger(__name__)


class BaseEngine(metaclass=ABCMeta):
    """
    所有推荐引擎的基类
    引擎是一个callable，调用获得推荐结果。
    """
    name = "所有推荐引擎的基类"

    def __init__(self, process, task_count):
        self.process = process
        self.task_count = task_count
        logger.debug(f'创建{self.name} {self.task_count}个')

    @abstractmethod
    def core_algo(self) -> List[Tuple[int, float, str]]:
        """
        算法核心抽象方法
        :return:
        """
        pass

    def recommend(self):
        """
        推荐内容
        :return:
        """
        result = self.core_algo()
        return result
