import logging
from random import shuffle

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
        self.len_jian = 0
        self.len_rand = 0

    def recommend(self):
        """
        推荐内容
        :return:
        """
        raise Exception

    def filter_content(self):
        """
        过滤内容
        :return:
        """
        raise Exception

    def order_content(self, jian_cids):
        """
        对内容进行排序
        :param jian_cids:
        :return:
        """
        shuffle(jian_cids)
