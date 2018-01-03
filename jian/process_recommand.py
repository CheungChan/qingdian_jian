from logzero import logger
from jian.engines.content_based_engine import ContentBasedEngine
from jian.engines.tag_based_engine import TagBasedEngine
from random import shuffle


class ProcessRecommand():

    def __init__(self, uid, n):
        self.uid = uid
        self.n = n
        self.dissed_cids = []
        self.combile_engine_recommad()
        self.filter_data()
        self.order_data()

    def combile_engine_recommad(self):
        logger.info('组合推荐引擎')
        data = []
        weight = {
            'ContentBasedEngine': 1,
            'TagBasedEngine': 1
        }
        for cls, w in weight.items():
            if w == 0:
                continue
            engine = eval(f'{cls}({self.uid},{self.n})')
            data += engine()
            self.dissed_cids += engine.dissed_cids
        self.data = data

    def filter_data(self):
        logger.info('过滤')
        data = []
        for cid, sim in self.data:
            if cid not in self.dissed_cids:
                data.append((cid, sim))
        self.data = data

    def order_data(self):
        logger.info('排序')
        self.data = [d[0] for d in self.data]
        shuffle(self.data)
        self.data = self.data[:self.n]

    def __call__(self, *args, **kwargs):
        return self.data
