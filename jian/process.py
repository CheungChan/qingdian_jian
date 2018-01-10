#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import logging
from collections import Counter
from math import ceil
from random import shuffle
from typing import List, Tuple

from jian import mongo_models
from jian.engines.content_based_engine import ContentBasedEngine
from jian.engines.hot_based_engine import HotBasedEngine
from jian.engines.tag_based_engine import TagBasedEngine
from qingdian_jian.settings import weight

logger = logging.getLogger(__name__)


class Process:
    """
    此类抽象出推荐的整个流程,会保存关于此用户的所有状态。首先组合过滤器根据各个推荐引擎所占的比重进行推荐并汇总推荐结果。
    然后对推荐结果进行过滤，然后排序，最后存储推荐结果。
    此类是一个callable的类，调用可以获得推荐结果。
    """
    engine_name_list = [c.__name__ for c in (ContentBasedEngine, TagBasedEngine, HotBasedEngine)]

    def __init__(self, uid, n):
        self.uid = uid
        self.n = n
        self.meta = {}
        self.rawdata: List[Tuple[int, float, str]] = []  # [(cid,sim,enginename),]
        self.data: List[int] = []
        self.prepare_prepare_signature_vector()
        self.combile_engine_recommad()
        self.filter_data()
        self.order_data()
        self.store_data()

    def prepare_prepare_signature_vector(self):
        # 所有被追踪（❤️）的内容id #所有被追踪（❤️）的标签id
        self.tracked_cids, self.tracked_tids = mongo_models.JianTrack.get_trackcids_tracktids(self.uid)
        # 所有不❤️的内容id  # 所有不❤️的标签id
        self.dissed_cids, self.dissed_tids = mongo_models.JianTrackDiss.get_track_disscids_diss_tids(self.uid)
        # 所有已推荐过的内容id
        self.jianed_cids = mongo_models.JianHistory.get_jian_history(self.uid)
        # 应该过滤的内容id
        self.fitering_cids = self.dissed_cids + self.jianed_cids
        self.len_tracked = len(self.tracked_cids)
        logger.debug(f'uid {self.uid} 找到cids个数 {self.len_tracked}')

    def combile_engine_recommad(self):
        """
        组合推荐引擎的思路是根据配置文件确定推荐引擎所占的比重，比重总和是1，根据比重求得每个推荐引擎应该推荐的
        个数。进行推荐，获取推荐的结果的个数，根据实际推荐的个数和应该推荐的个数求出缺少的个数。再下一个引擎推荐
        之间加上缺少的个数，进行推荐，依次循环。
        :return:
        """
        logger.info(f'组合推荐引擎self.n={self.n}')
        lack = 0

        for class_name, w in weight.items():
            if w == 0:
                continue
            task_count: int = ceil(self.n * w)
            task_count += lack
            # 调用推荐引擎的构造器
            self.check_engine_name(class_name)
            create_engine_code = f'{class_name}(self,{task_count})'
            engine = eval(create_engine_code)
            # 引擎是一个callable，调用获得推荐结果。
            newdata = engine.recommend()
            len_new = len(newdata)
            lack = (task_count - len_new)
            logger.info(f'引擎得到数据{len_new}条, 缺少={lack}')
            if len_new > 0:
                logger.info(f'{class_name}: {newdata}')
            self.rawdata += newdata

    def filter_data(self):
        logger.info('过滤')
        # 要过滤的cid
        rawdata = []
        for cid, sim, engine_name in self.rawdata:
            if cid not in self.fitering_cids:
                rawdata.append((cid, sim, engine_name))
        self.rawdata = rawdata

    def order_data(self):
        logger.info('排序')
        shuffle(self.rawdata)
        self.rawdata = self.rawdata[:self.n]
        self.data = list(set([d[0] for d in self.rawdata]))
        c = Counter(r[2] for r in self.rawdata)
        # 推荐的引擎来源和个数
        self.analyze = {'rate': self.rawdata, 'every_count': c.most_common(), 'counts': len(self.rawdata)}

    def store_data(self):
        logger.info('存储')
        mongo_models.JianHistory.store_tuijian_history(self.uid, self.data, self.analyze)

    @classmethod
    def check_engine_name(cls, class_name):
        if class_name not in cls.engine_name_list:
            raise Exception(f'引擎比例配置错误，{class_name}不存在')

    def __call__(self, *args, **kwargs):
        return {'jids': self.data}, self.analyze
