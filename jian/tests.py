# encoding=utf-8
import re
import sys

import jieba
from logzero import logger

sys.path.append("../")

jieba.load_userdict('userdict.txt')
import jieba.analyse
import jieba.posseg as pseg


def ignore_str(s: str) -> str:
    IGNORE_MATCH = re.compile('^\S+：|@\S+\s|cn：|服装：|con：')
    # 用户昵称|@xxx|cn:|服装:|con:
    at = IGNORE_MATCH.findall(s)
    logger.info(f'发现了匹配 {at}')
    for a in at:
        s = s.replace(a, '')
    return s


def no_stop_flag_str(s: str) -> list:
    stop_flag = ['x', 'c', 'u', 'd', 'p', 't', 'uj', 'm', 'f', 'r']
    words = pseg.cut(s)
    result = []
    for word, flag in words:
        if flag not in stop_flag:
            result.append(word)
    return result


def tf_idf_str(s) -> list:
    a = jieba.analyse.extract_tags(s, withWeight=True)
    return a


if __name__ == '__main__':
    s = "矮乐多Aliga：#路人女主的养成方法# #cos# 泽村·斯潘塞·英梨梨cn：@矮乐多Aliga Phx：@_Color卡拉 服装：@漫萌服饰 con：@cheese起司酱 每次看S02E10的这一个片段都会忍不住想哭，大概因为自己也曾经有过类似的经历吧，当喜欢的人不能再成为自己前进的动力而是会把自己一步步拖垮，我才知道是时候要放弃了。希望1p有还原出来，希望他日err也能找到属于自己的幸福，我可爱的小虎牙。"
    # s = '浮云长长长长长长长消'
    logger.info(f'原始s: {s}')
    s = ignore_str(s)
    logger.info(f'ignore之后s: {s}')
    a = no_stop_flag_str(s)
    logger.info(f'no_stop_flag_str:  {"/ ".join(a)}')
    jieba.del_word('自己')
    a = tf_idf_str(s)
    logger.info(f'tf_idf_str: {"/ ".join(r[0] for r in a)}')
