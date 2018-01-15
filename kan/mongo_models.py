#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 12:24
# @Author  : 陈章
import logging
from jian import mongo_models

logger = logging.getLogger(__name__)


class Statistics:
    @classmethod
    def get_data(cls, from_datetime, end_datetime):
        jianed_docs = mongo_models.JianHistory.statistics_rencent_jianed_docs(from_datetime, end_datetime)
        tracked_docs = mongo_models.JianTrack.statistics_rencent_tracked_docs(from_datetime, end_datetime)
        dissed_docs = mongo_models.JianTrackDiss.statistics_rencent_dissed_docs(from_datetime, end_datetime)
        jianed_cids = []
        for d in jianed_docs:
            jianed_cids += d.get('jids', 0)
        jianed_cids = list(set(jianed_cids))
        tracked_cids = list(set(d.get('cid', 0) for d in tracked_docs))
        dissed_cids = list(set(d.get('cid', 0) for d in dissed_docs))
        return jianed_cids, tracked_cids, dissed_cids
