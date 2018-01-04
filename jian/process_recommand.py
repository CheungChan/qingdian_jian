from logzero import logger
from jian.engines.content_based_engine import ContentBasedEngine
from jian.engines.tag_based_engine import TagBasedEngine
from jian.engines.hot_based_engine import HotBasedEngine
# 两个导入不能去掉，因为用到了eval
from random import shuffle
from qingdian_jian.settings import weight
from math import ceil
from typing import List
from jian.views.tuijian_util import store_tuijian_history


class ProcessRecommand():

    def __init__(self, uid, n):
        self.uid = uid
        self.n = n
        self.dissed_cids = []
        self.jianed_cids = []
        self.meta = {}
        self.rawdata: List[tuple[int, float, str]] = []  # [(cid,sim,enginename),]
        self.data: List[int] = []
        self.combile_engine_recommad()
        self.filter_data()
        self.order_data()
        self.store_data()

    def combile_engine_recommad(self):
        logger.info('组合推荐引擎')

        for cls, w in weight.items():
            if w == 0:
                continue
            n = ceil(self.n * w)
            logger.info(f'n={n}')
            create_engine_code = f'{cls}({self.uid},{n})'
            logger.info(create_engine_code)
            engine = eval(create_engine_code)
            self.rawdata += engine()
            logger.info(f'{cls}: {self.rawdata}')
            self.dissed_cids += engine.dissed_cids
            self.jianed_cids += engine.jianed_cids

    def filter_data(self):
        logger.info('过滤')
        # 要过滤的cid
        no_cids = self.dissed_cids + self.jianed_cids
        rawdata = []
        for cid, sim, engine_name in self.rawdata:
            if cid not in no_cids:
                rawdata.append((cid, sim, engine_name))
        self.rawdata = rawdata
        self.data = list(set([d[0] for d in self.rawdata]))

    def order_data(self):
        logger.info('排序')
        shuffle(self.data)
        self.data = self.data[:self.n]

    def store_data(self):
        logger.info('存储')
        store_tuijian_history(self.uid, self.data)

    def __call__(self, *args, **kwargs):
        return self.data, self.rawdata
