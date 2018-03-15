import json
import os
import sys
import time
from math import sqrt
from typing import Dict, List, Tuple

import logzero
from logzero import logger
from tqdm import tqdm

pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd + '../')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qingdian_jian.settings")

import django

django.setup()
from jian import models, mongo_models
from qingdian_jian.settings import DEBUG

logfile = f"/tmp/{os.path.basename(__file__)}.log"
logzero.logfile(logfile, encoding='utf-8', maxBytes=500_0000, backupCount=3)
print(f'脚本 DEBUG={DEBUG}')
time.sleep(2)


def get_content_user_grade() -> Dict[int, Dict[int, int]]:
    """
    得到内容 用户 评分的字典
    :return:
    """
    all_cids = models.Contents.get_all_normal_cids()
    all_uids = models.User.get_all_userids()
    content_user_grade = {}
    for uid in tqdm(all_uids, desc='get_content_user_grade'):
        tracked_cids = mongo_models.JianTrack.get_trackedcids(uid)
        for cid in tracked_cids:
            if cid in all_cids:
                content_user_grade.setdefault(cid, {}).setdefault(uid, 0)
                content_user_grade[cid][uid] += 1
    return content_user_grade


def get_user_content_grade(content_user_grade: Dict[int, Dict[int, int]]) -> Dict[int, Dict[int, int]]:
    """
    得到用户 内容 评分的字典
    :param content_user_grade:
    :return:
    """
    user_content_grade = {}
    for content, user_grade in tqdm(content_user_grade.items(), desc='get_user_content_grade'):
        for user, grade in user_grade.items():
            user_content_grade.setdefault(user, {}).setdefault(content, grade)
    return user_content_grade


def sim_distance(content_user_grade: Dict[int, Dict[int, int]], content1: int, content2: int) -> float:
    """
    使用欧几里得距离计算两个内容的评分之间的距离.
    :param content_user_grade:
    :param content1:
    :param content2:
    :return:
    """
    # 得到一个share user 的列表
    si = {}
    for user in content_user_grade[content1]:
        if user in content_user_grade[content2]:
            si[user] = 1
            break
    # 如果两者没有共同之处,则返回0
    if len(si) == 0: return 0
    # 计算所有被人评过分了的差值的平方和
    sum_of_squares = sum(pow(content_user_grade[content1][user] - content_user_grade[content2][user], 2) for user in
                         content_user_grade[content1] if user in content_user_grade[content2])
    return 1 / (1 + sqrt(sum_of_squares))


def top_matches(content_user_grade: Dict[int, Dict[int, int]], content: int) -> List[Tuple[float, int]]:
    """
    从字典中返回最为匹配的content.
    e.g
    content_user_grade中 content是10197的值为{1: 1, 6: 5, 7: 1, 9: 4, 10: 11, 17: 28, 32: 12, 34: 28, 43: 1, 58: 3, 83: 1, 86: 4, 91: 3}
    而 content是10700的值为{58: 3}
    因为两个content都被用户58评为3分,所以两个内容相似度为1.0
    :param content_user_grade:
    :param content:
    :param n:
    :param similarity:
    :return:
    """
    scores = [(sim_distance(content_user_grade, content, other), other) for other in
              content_user_grade
              if
              other != content]
    # 将匹配程度为0的内容过滤掉,这种内容可能是没有人点击过的内容,无法通过协同过滤进行推荐
    scores = list(filter(lambda sim_content: sim_content[0] > 0, scores))
    # 对列表进行排序,评价值最高者排在最前面
    scores.sort()
    scores.reverse()
    return scores


def calculate_content_similarity(content_user_grade: Dict[int, Dict[int, int]]) \
        -> Dict[int, List[Tuple[float, int]]]:
    """
    离线计算出内容和与该内容最相似的内容,来进行基于内容的协同过滤推荐.
    :param content_user_grade:
    :return:
    """
    # 建立字典,以给出与整合写物品最为相近的所有其他物品
    content_similarity = {}
    for content in tqdm(content_user_grade, desc='calculate_content_similarity'):
        # 针对大数据集更新状态变量
        scores = top_matches(content_user_grade, content)
        content_similarity[content] = scores
    return content_similarity


def get_record_from_mongo():
    content_user_grade = mongo_models.CollaborativeFiltering.get_content_user_grade()
    user_content_grade = mongo_models.CollaborativeFiltering.get_user_content_grade()
    content_similarity = mongo_models.CollaborativeFiltering.get_content_similarity()
    logger.info(len(content_user_grade))
    logger.info(len(user_content_grade))
    logger.info(len(content_similarity))


def main():
    """
    :return:
    """
    content_user_grade = get_content_user_grade()
    mongo_models.CollaborativeFiltering.set_content_user_grade(content_user_grade)
    user_content_grade = get_user_content_grade(content_user_grade)
    mongo_models.CollaborativeFiltering.set_user_content_grade(user_content_grade)
    content_similarity = calculate_content_similarity(content_user_grade)
    mongo_models.CollaborativeFiltering.set_content_similarity(content_similarity)


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'show':
        get_record_from_mongo()
    else:
        main()
