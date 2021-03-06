#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章
import logging
from collections import Counter
from typing import List, Tuple

from jian import models
from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override

logger = logging.getLogger(__name__)


class TagBasedEngine(BaseEngine):
    name = '基于标签的推荐引擎'

    def __init__(self, process, task_count):
        super(TagBasedEngine, self).__init__(process, task_count)

    @override
    def core_algo(self):
        """
        基于标签，使用标签所占比例进行推荐。
        :return:
        """
        if self.process.len_tracked == 0:
            return []
        result: List[Tuple[int, float, str]] = []
        # 所有浏览记录里面的tid和要出现几个cid
        c = Counter(self.process.tracked_tids)
        most_common = c.most_common()
        # logger.debug(f'most_common {most_common}')
        # 如 [(1, 16), (2, 14), (7, 14), (8, 14), (11, 14), (13, 5), (4, 2), (9, 2)]
        s = sum(c.values())  # 总的标签个数
        tid_roundnum = [[t[0], round(t[1] / s * self.task_count)] for t in most_common]
        # 需要某标签的个数 = 某标签浏览的次数 / 所有标签浏览次数 * 需要的个数
        # logger.debug(f'tid_roundnum= {tid_roundnum}')
        # 如 tid_num= [[1, 4], [2, 3], [7, 3], [8, 3], [11, 3], [13, 1], [4, 0], [9, 0]]

        # 取正好要的n个 由于most_common元素的第1（从0开始）个元素是四舍五入的结果，如果加起来的和大于n，跳过，最后再处理，
        # 如果加起来小于n，则加在第0个（从0开始）上面。
        num = 0
        tid_num = []
        for t in tid_roundnum:
            tid_num.append(t)
            num += t[1]  # 统计有了多少个标签了
            if num > self.task_count:
                break
        # 不再对最多的标签加缺少的。
        # else:
        #     logger.debug(f'四舍五入少了，加上{self.task_count-num}')
        #     tid_num[0][1] += self.task_count - num
        # logger.debug(f'tid_num= {tid_num}')
        # 获得数据库中tid对应的所有cids
        for tid, limit in tid_num:
            if limit == 0:
                continue
            all_jianed_cids = self.process.jianed_cids + [r[0] for r in result]
            cids = models.ContentsTag.get_limit_cids(tid, all_jianed_cids, self.process.dissed_cids, limit)
            for c in cids:
                sim = limit / len(cids) / self.task_count
                result.append((c, sim, self.__class__.__name__))
        return result
