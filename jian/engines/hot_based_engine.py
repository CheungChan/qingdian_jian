#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging

from jian import mongo_models
from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override

logger = logging.getLogger(__name__)


class HotBasedEngine(BaseEngine):
    name = '基于热门（流行度）的推荐引擎'

    def __init__(self, process, task_count):
        super(HotBasedEngine, self).__init__(process, task_count)

    @override
    def core_algo(self):
        """
        基于近期热门进行推荐
        :return:
        """
        cid_sim = mongo_models.JianTrack.get_recently_hot_tracked(limit=self.task_count,
                                                                  nocids=self.process.fitering_cids)
        result = [(cid, sim, self.__class__.__name__) for cid, sim in cid_sim]
        return result
