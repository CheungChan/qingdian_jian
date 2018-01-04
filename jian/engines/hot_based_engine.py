from logzero import logger
from collections import Counter
from typing import List, Tuple

from jian import models
from jian.engines.base_engine import BaseEngine
from qingdian_jian.utils import override


class HotBaseEngine(BaseEngine):
    """
    基于热门（流行度）的推荐引擎
    """

    def __init__(self, uid, n):
        logger.debug('创建基于热门（流行度）的引擎')
        super(HotBaseEngine, self).__init__(uid, n)

    @override
    def core_algo(self):
        result: List[Tuple[int, float, str]] = []

        return result
