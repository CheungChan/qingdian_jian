#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 12:24
# @Author  : 陈章
import logging
from jian import mongo_models
from qingdian_jian.utils import filter_cids

logger = logging.getLogger(__name__)


class Statistics:
    @classmethod
    def get_data(cls, from_datetime, end_datetime, client: int):
        jianed_docs = mongo_models.JianHistory.statistics_rencent_jianed_docs(from_datetime, end_datetime,client)
        tracked_docs = mongo_models.JianTrack.statistics_rencent_tracked_docs(from_datetime, end_datetime, client)
        dissed_docs = mongo_models.JianTrackDiss.statistics_rencent_dissed_docs(from_datetime, end_datetime, client)
        jianed_cids = []
        for d in jianed_docs:
            jianed_cids += d.get('jids', 0)
        jianed_cids = filter_cids(jianed_cids)
        tracked_cids = filter_cids(d.get('cid', 0) for d in tracked_docs)
        dissed_cids = filter_cids(d.get('cid', 0) for d in dissed_docs)
        return jianed_cids, tracked_cids, dissed_cids
