from django.urls import path
from jian.views import diss, track, tuijian

urlpatterns = [
    path('track', track.track),
    path('track/diss', diss.track_diss),
    path('diss/list', diss.diss_list),
    path('uids_by_uid', tuijian.uids_by_uid),
    path('cids_by_uid', tuijian.cids_by_uid),
    path('uids_by_cid', tuijian.uids_by_cid),
    path('cids_by_cid', tuijian.cids_by_cid),
]
