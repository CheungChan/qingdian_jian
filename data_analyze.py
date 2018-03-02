import os
from datetime import datetime, timedelta
from prettytable import PrettyTable

import logzero

from qingdian_jian.settings import DEBUG
from qingdian_jian.utils import get_mongo_collection

logfile = f"/tmp/{os.path.basename(__file__)}.log"
logzero.logfile(logfile, encoding='utf-8', maxBytes=500_0000, backupCount=3)
print(f'脚本DEBUG={DEBUG}')


def get_mongo_record(from_datetime, end_datetime):
    jian_history_db = get_mongo_collection('jian_history')
    jian_track_db = get_mongo_collection('jian_track')
    jian_track = {}
    jian_history = {}
    if from_datetime and end_datetime:
        condition = {'update_time': {'$gte': from_datetime, '$lte': end_datetime}}
    else:
        condition = {}
    for j in jian_track_db.find(condition):
        jian_track.setdefault(j['uid'], set()).add(j['cid'])
    for j in jian_history_db.find(condition):
        for jid in j['jids']:
            jian_history.setdefault(j['uid'], set()).add(jid)
    return jian_history, jian_track


if __name__ == '__main__':
    if DEBUG:
        from_datetime = None
        end_datetime = None
    else:
        from_datetime = datetime.now() - timedelta(days=1)
        end_datetime = datetime.now()

    jian_history, jian_track = get_mongo_record(from_datetime=from_datetime, end_datetime=end_datetime)

    records = []
    for uid in jian_track.keys():
        track_count = len(jian_track[uid])
        history_count = len(jian_history.get(uid, []))
        if history_count == 0:
            continue
        data = [uid, history_count, track_count, f'{track_count / history_count * 100}%']
        records.append(data)
    records.sort(key=lambda record: record[2], reverse=True)
    t = PrettyTable(['用户id', '推荐个数', '喜欢个数', '命中率'])
    t.align['用户id'] = 'l'
    t.align['推荐个数'] = 'l'
    t.align['喜欢个数'] = 'l'
    t.align['命中率'] = 'r'
    for r in records:
        t.add_row(r)
    print(t)
