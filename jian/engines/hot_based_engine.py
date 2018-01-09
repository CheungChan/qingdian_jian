#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import logging

from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override
from jian.utils import get_recently_hot_tracked

logger = logging.getLogger(__name__)


class HotBasedEngine(BaseEngine):
    name = '基于热门（流行度）的推荐引擎'

    def __init__(self, uid, n):
        logger.debug(f'创建{self.name}')
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
