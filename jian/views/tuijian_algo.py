import logging
from collections import Counter
from random import shuffle

from jian import models
from jian.views.tuijian_util import get_trackcids_tracktids, get_track_disscids_diss_tids, get_jian_history

logger = logging.getLogger(__name__)


def algo_jian_by_tag(uid, n):
    # 找到此用户的浏览记录
    _, tracked_tids = get_trackcids_tracktids(uid)
    all_diss_cids, _ = get_track_disscids_diss_tids(uid)
    has_jianed_ids = get_jian_history(uid)
    len_tracked = len(tracked_tids)
    logger.info(f'uid {uid} 找到tids个数 {len_tracked}')
    if len_tracked == 0:
        jian_cids = []
    else:
        # 所有浏览记录里面的tid和要出现几个cid
        c = Counter(tracked_tids)
        most_common = c.most_common()
        logger.info(f'most_common {most_common}')
        # 如 [(1, 16), (2, 14), (7, 14), (8, 14), (11, 14), (13, 5), (4, 2), (9, 2)]
        s = sum(c.values())  # 总的标签个数
        tid_roundnum = [[t[0], round(t[1] / s * n)] for t in most_common]
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
            if num > n:
                break
        else:
            logger.info(f'四舍五入少了，加上{n-num}')
            tid_num[0][1] += n - num
        logger.info(f'tid_num= {tid_num}')
        # 获得数据库中tid对应的所有cids
        jian_cids = []
        for tid, limit in tid_num:
            if limit == 0:
                continue
            all_jianed_cids = has_jianed_ids + jian_cids
            cids = models.ContentsTag.get_limit_cids(tid, all_jianed_cids, all_diss_cids, limit)
            jian_cids += cids
        jian_cids = list(set(jian_cids))[:n]
    len_jian = len(jian_cids)
    logger.info(f'获得推荐{len_jian}个')
    len_lack = n - len_jian
    if len_lack > 0:
        all_jianed_cids = has_jianed_ids + jian_cids
        jian_cids += models.ContentsTag.get_limit_cids(None, all_jianed_cids, all_diss_cids, len_lack)
        logger.info(f'不够，从最新中获取{len_lack}个')
    if len(jian_cids) < n:
        logger.info('用户看完了所有内容，随机选取内容')
        len_lack = n
        jian_cids = models.ContentsTag.get_limit_cids(None, None, all_diss_cids, len_lack)
    shuffle(jian_cids)
    return {'jids': jian_cids, 'j': len_jian, 'n': len_lack}
