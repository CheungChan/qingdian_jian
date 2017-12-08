from django.urls import path
from jian import views

urlpatterns = [
    path('track', views.track),
    path('track/diss', views.track_diss),
    path('uids_by_uid', views.uids_by_uid),
    path('cids_by_uid', views.cids_by_uid),
    path('uids_by_cid', views.uids_by_cid),
    path('cids_by_cid', views.cids_by_cid),
]
