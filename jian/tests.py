#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

import re
import sys
from math import sqrt
import jieba
from logzero import logger

sys.path.append("../")

jieba.load_userdict('userdict.txt')
import jieba.analyse
import jieba.posseg as pseg


def ignore_str(s: str) -> str:
    """
    去除字符串中的非人类语言
    :param s:
    :return:
    """
    IGNORE_MATCH = re.compile('^\S+：|@\S+\s|cn：|服装：|con：')
    # 用户昵称|@xxx|cn:|服装:|con:
    at = IGNORE_MATCH.findall(s)
    logger.info(f'去除非人类语言，发现了匹配 {at}')
    for a in at:
        s = s.replace(a, '')
    return s


def no_stop_flag_str(s: str, stop_flag=None) -> list:
    """
    去除特定词性
    :param s:
    :param stop_flag 要去除的词性列表
    :return:
    """
    if not stop_flag:
        stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']
    words = pseg.cut(s)
    result = []
    for word, flag in words:
        if flag not in stop_flag:
            result.append(word)
    return result


def tf_idf_str(s, topK=20, withWeight=True, ignore=True) -> list:
    """
    使用TF-IDF算法，去除关键词
    :param s:
    :param topK:
    :param withWeight: 返回值是否带关键词的权重
    :return:
    """
    if ignore:
        s = ignore_str(s)
    a = jieba.analyse.extract_tags(s, withWeight=withWeight, topK=topK)
    logger.info(a)
    return a


def text_rank_str(s, topK=20, withWeight=True) -> list:
    """
    使用text_rank算法，其余同tf_idf_str
    :param s:
    :param topK:
    :param withWeight:
    :return:
    """
    a = jieba.analyse.textrank(s, withWeight=withWeight, topK=topK)
    return a


def merge_tag(tag1=None, tag2=None):
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


def dot_product(v1, v2):
    """
    计算矩阵的点积
    :param v1:
    :param v2:
    :return:
    """
    return sum(a * b for a, b in zip(v1, v2))


def magnitude(vector):
    return sqrt(dot_product(vector, vector))


def similarity(f1: list, f2: list) -> float:
    """
    计算余弦相似度
    :param f1: 以(关键词,词频)为元素的列表1
    :param f2: 以(关键词,词频)为元素的列表2
    :return:
    """
    return dot_product(f1, f2) / (magnitude(f1) * magnitude(f2) + 0.00000001)


if __name__ == '__main__':
    content1 = u"""
                    可月付 无中介 方庄地铁附近 芳城园一区单间出租
                    我的房子在方庄地铁附近的芳城园一区，正规小区楼房，
                    三家合住，现出租一间主卧和一间带小阳台次卧，室内家电齐全，
                    冰箱，洗衣机等都有，可洗澡上网，做饭都可以，小区交通便利，四通八达，
                    希望入住的是附近正常上班的朋友
                    """
    # https://www.douban.com/group/topic/93410328/
    content2 = u"""
                    可月付 无中介 方庄地铁附近 芳城园一区主卧次卧出租
                    我的房子在方庄地铁附近的芳城园一区，正规小区楼房，
                    三家合住，现出租一间主卧和一间带小阳台次卧，室内家电齐全，
                    冰箱，洗衣机等都有，可洗澡上网，做饭都可以，小区交通便利，四通八达，
                    希望入住的是附近正常上班的朋友
                    """

    # https://www.douban.com/group/topic/93410308/
    content3 = u"""方庄地铁附近 芳城园一区次卧出租
                        我的房子在方庄地铁附近的芳城园一区，正规小区楼房，
                        三家合住，现出租一间主卧和一间带小阳台次卧，室内家电齐全，
                        冰箱，洗衣机等都有，可洗澡上网，做饭都可以，小区交通便利，四通八达，
                        希望入住的是附近正常上班的朋友
                        """

    # https://www.douban.com/group/topic/93381171/
    content4 = u"""二环玉蜓桥旁下月27号后可入住二居
                    方庄方古园一区5号楼下月27日到期出租，
                    我是房主无中介费 ，新一年租6000元每月押一付三，主次卧可分开住。
                    距地铁5号线蒲黄榆站5分钟路程。房屋60平正向，另有看守固定车位。
                    """

    tag1 = tf_idf_str(content1)
    tag2 = tf_idf_str(content2)
    tag3 = tf_idf_str(content3)
    tag4 = tf_idf_str(content4)
    v1, v2 = merge_tag(tag1, tag2)
    print('content1 和 content2 相似度为: %s' % similarity(v1, v2))

    v1, v3 = merge_tag(tag1, tag3)
    print('content1 和 content3 相似度为: %s' % similarity(v1, v3))

    v2, v3 = merge_tag(tag2, tag3)
    print('content2 和 content3 相似度为: %s' % similarity(v2, v3))

    v2, v4 = merge_tag(tag2, tag4)

    print('content2 和 content4 相似度为: %s' % similarity(v2, v4))
