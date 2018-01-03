import logging
from collections import Counter

from jian import models
from jian.engines.base_engine import BaseEngine

logger = logging.getLogger(__name__)


class TagBasedEngine(BaseEngine):
    """
    基于标签的推荐引擎
    """

    def __init__(self, uid, n):
        super(TagBasedEngine, self).__init__(uid, n)

    def recommend(self):
        result_cids = []
        len_tracked = len(self.tracked_tids)
        logger.info(f'uid {self.uid} 找到tids个数 {len_tracked}')
        if len_tracked == 0:
            pass
        else:
            result_cids = self.algo_recommand_by_tag(result_cids)
        result_cids = self.add_rand_cids(result_cids)
        self.order_content(result_cids)
        return {'jids': result_cids, 'j': self.len_jian, 'n': self.len_rand}

    def algo_recommand_by_tag(self, result_cids):
        # 所有浏览记录里面的tid和要出现几个cid
        c = Counter(self.tracked_tids)
        most_common = c.most_common()
        logger.info(f'most_common {most_common}')
        # 如 [(1, 16), (2, 14), (7, 14), (8, 14), (11, 14), (13, 5), (4, 2), (9, 2)]
        s = sum(c.values())  # 总的标签个数
        tid_roundnum = [[t[0], round(t[1] / s * self.n)] for t in most_common]
        # 需要某标签的个数 = 某标签浏览的次数 / 所有标签浏览次数 * 需要的个数
        logger.info(f'tid_roundnum= {tid_roundnum}')
        # 如 tid_num= [[1, 4], [2, 3], [7, 3], [8, 3], [11, 3], [13, 1], [4, 0], [9, 0]]

        # 取正好要的n个 由于most_common元素的第1（从0开始）个元素是四舍五入的结果，如果加起来的和大于n，跳过，最后再处理，
        # 如果加起来小于n，则加在第0个（从0开始）上面。
        num = 0
        tid_num = []
        for t in tid_roundnum:
            tid_num.append(t)
            num += t[1]  # 统计有了多少个标签了
            if num > self.n:
                break
        else:
            logger.info(f'四舍五入少了，加上{self.n-num}')
            tid_num[0][1] += self.n - num
        logger.info(f'tid_num= {tid_num}')
        # 获得数据库中tid对应的所有cids
        for tid, limit in tid_num:
            if limit == 0:
                continue
            all_jianed_cids = self.jianed_cids + result_cids
            cids = models.ContentsTag.get_limit_cids(tid, all_jianed_cids, self.dissed_cids, limit)
            result_cids += cids
        result_cids = list(set(result_cids))[:self.n]
        return result_cids

    def add_rand_cids(self, result_cids):
        """
        添加随机的内容id，一方面增加惊喜度，一方面补充不够的内容id。
        :param result_cids:
        :return:
        """
        len_jian = len(result_cids)
        logger.info(f'获得推荐{len_jian}个')
        len_rand = self.n - len_jian
        if len_rand > 0:
            all_jianed_cids = self.jianed_cids + result_cids
            result_cids += models.ContentsTag.get_limit_cids(None, all_jianed_cids, self.dissed_cids, len_rand)
            logger.info(f'不够，从最新中获取{len_rand}个')
        if len(result_cids) < self.n:
            logger.info('用户看完了所有内容，随机选取内容')
            len_rand = self.n
            result_cids = models.ContentsTag.get_limit_cids(None, None, self.dissed_cids, len_rand)
        self.len_jian = len_jian
        self.len_rand = len_rand
        return result_cids
