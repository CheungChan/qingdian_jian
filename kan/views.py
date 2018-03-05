from datetime import datetime, timedelta

from django.shortcuts import render, HttpResponse

from kan import mongo_models
from jian import models
from qingdian_jian.utils import type_cast_request_args, log_views
from qingdian_jian.settings import DEBUG


@log_views
def index(request):
    validaters = [('datetime_range', '', str),
                  ('client', None, int)]
    datetime_range, client = type_cast_request_args(request, validaters)
    if datetime_range:
        from_datetime, end_datetime = datetime_range.split(' - ')
        from_datetime = datetime.strptime(from_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
    else:
        from_datetime = datetime.now() - timedelta(days=30)
        end_datetime = datetime.now()
    jianed_cids, tracked_cids, dissed_cids = mongo_models.Statistics.get_data(from_datetime, end_datetime, client)
    len_jianed_cids = len(jianed_cids)
    len_tracked_cids = len(tracked_cids)
    len_dissed_cids = len(dissed_cids)
    len_nothing_cids = len_jianed_cids - len_tracked_cids - len_dissed_cids
    if len_nothing_cids < 0:
        len_nothing_cids = 0
    return render(request, 'jian/kan/index.html', locals())


@log_views
def data_analyze(request):
    sort = request.GET.get('sort', '2')
    validaters = [('sort', 2, int)]
    sort, = type_cast_request_args(request, validaters)
    if not 0 <= sort <= 3:
        return HttpResponse('参数错误')
    if DEBUG:
        from_datetime = None
        end_datetime = None
    else:
        from_datetime = datetime.now() - timedelta(days=1)
        end_datetime = datetime.now()
    jian_history, jian_track = mongo_models.Statistics.data_analyze(from_datetime, end_datetime)

    records = []
    for uid in jian_track.keys():
        track_count = len(jian_track[uid])
        history_count = len(jian_history.get(uid, []))
        if history_count == 0:
            continue
        user_name = models.User.get_username_by_uid(uid)
        data = [user_name if user_name else '', history_count, track_count,
                round(track_count / history_count * 100, 2)]
        records.append(data)
    records.sort(key=lambda record: record[sort], reverse=True)
    return render(request, 'jian/kan/data_analyze.html', locals())
