#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging

from jian import models
from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override

logger = logging.getLogger(__name__)


class RecentBasedEngine(BaseEngine):
    name = '基于最近更新的推荐引擎'

    def __init__(self, process, task_count):
        super(RecentBasedEngine, self).__init__(process, task_count)

    @override
    def core_algo(self):
        """
        基于最近更新进行推荐
        :return:
        """
        cid_sim = models.Contents.get_recently_cids(limit=self.task_count, nocids=self.process.fitering_cids)
        result = [(cid, sim, self.__class__.__name__) for cid, sim in cid_sim]
        return result
