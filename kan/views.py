from django.http import JsonResponse
from django.shortcuts import render
from kan import mongo_models
from datetime import datetime, timedelta
from qingdian_jian.utils import trans_int, MongoDocEncoder


def index(request):
    datetime_range = request.GET.get('datetime_range', '')
    if datetime_range:
        from_datetime, end_datetime = datetime_range.split(' - ')
        from_datetime = datetime.strptime(from_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
    else:
        from_datetime = datetime.now() - timedelta(days=7)
        end_datetime = datetime.now()
    jianed_cids, tracked_cids, dissed_cids = mongo_models.Statistics.get_data(from_datetime, end_datetime)
    len_jianed_cids = len(jianed_cids)
    len_tracked_cids = len(tracked_cids)
    len_dissed_cids = len(dissed_cids)
    len_nothing_cids = len_jianed_cids - len_tracked_cids - len_dissed_cids
    return render(request, 'kan/index.html', locals())
