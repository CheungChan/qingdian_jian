import json
import logging
import os
from functools import lru_cache
from math import sqrt

import jieba
import pymysql

from qingdian_jian.utils import cache_redis
from qingdian_jian.settings import DEBUG

print(f'脚本DEBUG={DEBUG}')
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
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


def get_connection():
    connection = pymysql.connect(**BL_MYSQL_CONF)
    return connection


class Contents_Calculate:
    @classmethod
    @lru_cache()
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
    @lru_cache()
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


def main():
    connection = get_connection()
    all_contents: [int, str] = {}
    with connection.cursor() as cursor:
        cursor.execute(GET_ALL_CONTENTS_SQL)
        result = cursor.fetchall()
        for cid, title, desp in result:
            all_contents[cid] = title + ' ' + desp
    all_contents_copy = all_contents.copy()
    for cid1, desp1 in all_contents.items():
        name = f'azhang_jian_simi_{cid1}'
        cached_value = cache_redis(name)
        if cached_value:
            logger.info(f'{name} redis中已存在')
            continue
        l = list()
        for cid2, desp2 in all_contents_copy.items():
            if cid1 == cid2:
                continue
            simi = Contents_Calculate.str_similarity(desp1, desp2)
            if not 0.0 < simi < 9.9:
                continue
            l.append((cid2, simi))
        if len(l) == 0:
            logging.warning(f'{name} 无相似内容')
        l.sort(key=lambda cid_simi_tuple: cid_simi_tuple[1], reverse=True)
        value_func = lambda: json.dumps(l)
        retrive_value_func = lambda l: json.loads(l)
        cached_value = cache_redis(name, value_func, retrive_value_func)
        logger.info(f'{name}: {cached_value}')


if __name__ == '__main__':
    main()
