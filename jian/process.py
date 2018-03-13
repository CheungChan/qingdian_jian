#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import logging
from collections import Counter
from math import ceil
from random import shuffle
from typing import List, Tuple

from jian import mongo_models, models
from jian.engines.content_based_engine import ContentBasedEngine
from jian.engines.hot_based_engine import HotBasedEngine
from jian.engines.tag_based_engine import TagBasedEngine
from jian.engines.recent_based_engine import RecentBasedEngine
from jian.engines.cf_user_based_engine import CFUserBasedEngine
from jian.engines.cf_content_based_engine import CFContentBasedEngine
from qingdian_jian.settings import weight

logger = logging.getLogger(__name__)


class Process:
    """
    此类抽象出推荐的整个流程,会保存关于此用户的所有状态。首先组合过滤器根据各个推荐引擎所占的比重进行推荐并汇总推荐结果。
    然后对推荐结果进行过滤，然后排序，最后存储推荐结果。
    此类是一个callable的类，调用可以获得推荐结果。
    """
    engine_name_list = [c.__name__ for c in
                        (ContentBasedEngine, TagBasedEngine, HotBasedEngine, RecentBasedEngine, CFUserBasedEngine,
                         CFContentBasedEngine)]

    def __init__(self, uid, n, client, device_id):
        self.uid = uid
        self.n = n
        self.client = client
        self.device_id = device_id
        self.meta = {}
        self.rawdata: List[Tuple[int, float, str]] = []  # [(cid,sim,enginename),]
        self.data: List[int] = []
        self.prepare_prepare_signature_vector()
        self.combile_engine_recommad()
        self.filter_data()
        self.variaty_data()
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
        self.fitering_cids = list(
            set(self.dissed_cids + self.jianed_cids + self.tracked_cids + models.Contents.get_all_abnormal_cids()))
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
            if lack > 0:
                logger.info(f'引擎应得{task_count}个,实得{len_new}个,缺少={lack}个')
            if len_new > 0:
                logger.info(f'{class_name}全部OK: {newdata}')
            self.rawdata += newdata

    def filter_data(self):
        logger.info('过滤')
        # logger.info(f'过滤前self.rawdata={self.rawdata}')
        # 要过滤的cid
        filtered_rawdata = []
        for cid, sim, engine_name in self.rawdata:
            if cid not in self.fitering_cids:
                filtered_rawdata.append((cid, sim, engine_name))

        # 对pic_link相同(有内容)的去重,pic_link为空算都是不重的.
        pic_link_cid_dict = {}
        no_pick_link_cid_list = []
        for data in filtered_rawdata:
            pic_link = models.Contents.get_pic_link_by_id(data[0])
            if not pic_link:
                no_pick_link_cid_list.append(data)
            pic_link_cid_dict[pic_link] = data
        self.rawdata = list(set([v for v in pic_link_cid_dict.values()] + no_pick_link_cid_list))
        # logger.info(f'过滤后self.rawdata={self.rawdata}')

    def variaty_data(self):
        """
        为了维持推荐的多样性,同一主题在一次推荐下不要多于MAX_CID_PER_THEME个.
        :return:
        """
        logger.info('多样性')
        MAX_CID_PER_THEME = 3
        theme_count = {}
        new_rawdata = []
        for cid, sim, engine_name in self.rawdata:
            theme = models.Contents.get_theme_by_cid(cid)
            theme_count.setdefault(theme, 0)
            theme_count[theme] += 1
            if theme_count[theme] <= MAX_CID_PER_THEME:
                new_rawdata.append((cid, sim, engine_name))
        self.rawdata = new_rawdata

    def order_data(self):
        logger.info('排序')
        self.rawdata = self.rawdata[:self.n]
        shuffle(self.rawdata)
        self.data = [d[0] for d in self.rawdata]
        c = Counter(d[2] for d in self.rawdata)
        # 推荐的引擎来源和个数
        self.analyze = {'rate': self.rawdata, 'every_count': c.most_common(), 'counts': len(self.rawdata),
                        'client': self.client, 'device_id': self.device_id}

    def store_data(self):
        logger.info('存储')
        mongo_models.JianHistory.store_tuijian_history(self.uid, self.data, self.analyze)

    @classmethod
    def check_engine_name(cls, class_name):
        if class_name not in cls.engine_name_list:
            raise Exception(f'引擎比例配置错误，{class_name}不存在')

    def __call__(self, *args, **kwargs):
        return {'jids': self.data, 'uid': self.uid}, self.analyze
