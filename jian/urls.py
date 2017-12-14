from django.urls import path
from jian.views import diss, track, tuijian

urlpatterns = [
    path('track', track.track),
    path('track/diss', diss.track_diss),
    path('diss/list', diss.diss_list),
    path('cids_by_uid', tuijian.cids_by_uid),
    path('jian_history', tuijian.jian_history),
]
