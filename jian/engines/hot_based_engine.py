#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

from logzero import logger

from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override
from jian.utils import get_recently_hot_tracked


class HotBasedEngine(BaseEngine):
    """
    基于热门（流行度）的推荐引擎
    """

    def __init__(self, uid, n):
        logger.debug('创建基于热门（流行度）的引擎')
        super(HotBasedEngine, self).__init__(uid, n)

    @override
    def core_algo(self):
        """
        基于近期热门进行推荐
        :return:
        """
        nocids = self.jianed_cids + self.dissed_cids
        cid_sim = get_recently_hot_tracked(limit=self.n, nocids=nocids)
        result = [(cid, sim, self.__class__.__name__) for cid, sim in cid_sim]
        return result
