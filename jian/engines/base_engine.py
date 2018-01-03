import logging
from typing import Dict

from werkzeug.utils import cached_property

from jian.views.tuijian_util import get_trackcids_tracktids, get_track_disscids_diss_tids, get_jian_history

logger = logging.getLogger(__name__)


class BaseEngine():
    """
    所有推荐引擎的基类
    """

    @cached_property
    def tracked_cids(self):
        """
        :return: 所有被追踪（喜欢）的内容id
        """
        return get_trackcids_tracktids(self.uid)[0]

    @cached_property
    def tracked_tids(self):
        """
        :return: 所有被追踪（❤️）的标签id
        """
        return get_trackcids_tracktids(self.uid)[1]

    @cached_property
    def dissed_cids(self):
        """
        :return: 所有不❤️的内容id
        """
        return get_track_disscids_diss_tids(self.uid)[0]

    @cached_property
    def dissed_tids(self):
        """
        :return: 所有不❤️的标签id
        """
        return get_track_disscids_diss_tids(self.uid)[1]

    @cached_property
    def jianed_cids(self):
        """
        :return: 所有已推荐过的内容id
        """
        return get_jian_history(self.uid)

    def __init__(self, uid, n):
        """
        :param uid: 用户id
        :param n: 要获得推荐的个数
        :param len_jian 推荐算法得到的个数
        :param len_rand 随机得到的个数
        """
        self.uid = uid
        self.n = n
        self.prepare_signature_vector()

    def prepare_signature_vector(self):
        """
        生成用户特征向量
        :return:
        """
        self.len_tracked = len(self.tracked_tids)
        logger.info(f'uid {self.uid} 找到tids个数 {self.len_tracked}')

    def core_algo(self):
        """
        算法核心
        :return:
        """
        raise Exception

    def process_recommend(self):
        """
        推荐内容
        :return:
        """
        result: Dict[int, float] = {}
        if self.len_tracked == 0:
            pass
        else:
            result = self.core_algo()
        return result
