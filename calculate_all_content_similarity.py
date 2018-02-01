import os
import sys
import time
from datetime import datetime
from functools import lru_cache
from math import sqrt
from multiprocessing import Pool
from typing import Dict

import jieba
import pymysql
from logzero import logger

from qingdian_jian.settings import DEBUG
from qingdian_jian.utils import get_mongo_collection

print(f'脚本DEBUG={DEBUG}')
pwd = os.path.dirname(os.path.abspath(__name__))
userdict = os.path.join(pwd, 'userdict.txt')
jieba.load_userdict(userdict)
import jieba.analyse

test_db = {
    'db': 'qdbuluo',
    'host': '10.10.6.2',
    'user': 'develop',
    'password': '123-qwe',
    'charset': 'utf8mb4',

}
prod_db = {
    'db': 'qdbuluo',
    'host': '10.10.10.2',
    'port': 2000,
    'user': 'qd',
    'password': '123^%$-qwe-asd',
    'charset': 'utf8mb4',
}
BL_MYSQL_CONF = test_db if DEBUG else prod_db
GET_ALL_CONTENTS_SQL = "select id,title, desp from contents order by updated_at"
PROCESS_COUNT = os.cpu_count() - 1
# PROCESS_COUNT = 1
print(f'PROCESS_COUNT={PROCESS_COUNT}')
time.sleep(2)


def get_connection():
    connection = pymysql.connect(**BL_MYSQL_CONF)
    return connection


class Contents_Calculate:
    @classmethod
    @lru_cache(None)
    def tf_idf_str(cls, s: str, topK=20, withWeight=True) -> list:
        """
        使用TF-IDF算法，去除关键词
        :param s:
        :param topK:
        :param withWeight: 返回值是否带关键词的权重
        :return:
        """
        # if ignore:
        #     s = cls.ignore_str(s)
        a = jieba.analyse.extract_tags(s, withWeight=withWeight, topK=topK)
        # logger.debug(a)
        return a

    @classmethod
    def merge_tag(cls, tag1=None, tag2=None):
        v1 = []
        v2 = []
        tag_dict1 = {i[0]: i[1] for i in tag1}
        tag_dict2 = {i[0]: i[1] for i in tag2}
        merged_tag = set(list(tag_dict1.keys()) + list(tag_dict2.keys()))
        for i in merged_tag:
            if i in tag_dict1:
                v1.append(tag_dict1[i])
            else:
                v1.append(0)

            if i in tag_dict2:
                v2.append(tag_dict2[i])
            else:
                v2.append(0)
        return v1, v2

    @classmethod
    def dot_product(cls, v1, v2):
        """
        计算矩阵的点积
        :param v1:
        :param v2:
        :return:
        """
        return sum(a * b for a, b in zip(v1, v2))

    @classmethod
    def magnitude(cls, vector):
        return sqrt(cls.dot_product(vector, vector))

    @classmethod
    def similarity(cls, f1: list, f2: list) -> float:
        """
        计算余弦相似度
        :param f1: 以(关键词,词频)为元素的列表1
        :param f2: 以(关键词,词频)为元素的列表2
        :return:
        """
        return cls.dot_product(f1, f2) / (
                cls.magnitude(f1) * cls.magnitude(f2) + 0.00000001)

    @classmethod
    def str_similarity(cls, s1: str, s2: str) -> float:
        """
        求解两个字符串的相似度
        :param s1: 字符串1
        :param s2: 字符串2
        :return:
        """
        tag1 = cls.tf_idf_str(s1)
        tag2 = cls.tf_idf_str(s2)
        v1, v2 = cls.merge_tag(tag1, tag2)
        return cls.similarity(v1, v2)


def get_all_contents() -> Dict[int, str]:
    """
    拿到数据库中所有的内容的id和描述组成的dict
    :return:
    """
    connection = get_connection()
    all_contents: [int, str] = {}
    with connection.cursor() as cursor:
        cursor.execute(GET_ALL_CONTENTS_SQL)
        result = cursor.fetchall()
        for cid, title, desp in result:
            all_contents[cid] = title + ' ' + desp
    return all_contents


def calcuclate_simi_for_one(cid1: int, desp1: str, all_contents: Dict[int, str], need_update: bool):
    """
    计算内容id为cid1,内容描述为desp1与all_contents所有内容中每个的相似度
    :param cid1:
    :param desp1:
    :param all_contents:
    :param need_update: 已经计算过,是否更新
    :return:
    """
    db = get_mongo_collection("content_similarity_offline")
    cached_value = db.find_one({'cid': cid1})
    l = list()
    for cid2, desp2 in all_contents.items():
        if cid1 == cid2:
            continue
        # 计算好了的cid2和simi.
        cached_value_dict = {}
        if cached_value:
            logger.info(f'{cid1}已存在')
            if need_update:
                pass
            else:
                logger.info('返回')
                return
            cached_value_dict = {cid2_: simi_ for cid2_, simi_ in cached_value['cid2_sim']}

        # 相似度如果计算过直接取出,否则计算.
        simi = cached_value_dict.get(cid2)
        if simi is None:
            simi = Contents_Calculate.str_similarity(desp1, desp2)
            logger.info(f'进程{os.getpid()} 计算{cid1}  {cid2} 相似度 {simi}')
        else:
            # logger.debug(f'进程{os.getpid()} {cid1}  {cid2} 相似度{simi}直接取出')
            pass
        # if 0.0 < simi < 0.99:
        l.append((cid2, simi))
    if len(l) == 0:
        logger.warning(f'{cid1} 无相似内容')
    l.sort(key=lambda cid_simi_tuple: cid_simi_tuple[1], reverse=True)
    data = {'cid': cid1, 'cid2_sim': l, 'update_time': datetime.now()}
    # 已存在了就更新,没有就插入.
    db.update({'cid': cid1}, data, upsert=True)
    # logger.debug(data)
    logger.info(f'{cid1} 相似度计算完成')


def main(need_update):
    """
    使用进程池,开启多个进程计算相似度.
    :param need_update:
    :return:
    """
    p = Pool(PROCESS_COUNT)
    all_contents = get_all_contents()
    logger.info(f'总共{len(all_contents)}条内容')
    for cid1, desp1 in all_contents.items():
        p.apply_async(calcuclate_simi_for_one, args=(cid1, desp1, all_contents, need_update))
    p.close()
    p.join()


if __name__ == '__main__':
    """
    如果有参数-u则遇到计算过的更新,如果没有参数,直接跳过.
    """
    need_update = False
    if len(sys.argv) == 2 and sys.argv[1] == '-u':
        need_update = True
    start = time.time()
    main(need_update)
    end = time.time()
    logger.info(f'总执行时间{end-start}s')
