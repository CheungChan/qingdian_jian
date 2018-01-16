from datetime import datetime, timedelta

from django.shortcuts import render

from kan import mongo_models
from qingdian_jian.utils import trans_int


def index(request):
    datetime_range = request.GET.get('datetime_range', '')
    client = request.GET.get('client', '')
    if datetime_range:
        from_datetime, end_datetime = datetime_range.split(' - ')
        from_datetime = datetime.strptime(from_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
    else:
        from_datetime = datetime.now() - timedelta(days=30)
        end_datetime = datetime.now()
    client, = trans_int(client, )
    jianed_cids, tracked_cids, dissed_cids = mongo_models.Statistics.get_data(from_datetime, end_datetime, client)
    len_jianed_cids = len(jianed_cids)
    len_tracked_cids = len(tracked_cids)
    len_dissed_cids = len(dissed_cids)
    len_nothing_cids = len_jianed_cids - len_tracked_cids - len_dissed_cids
    return render(request, 'jian/kan/index.html', locals())
