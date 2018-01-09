#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

from django.urls import path

from jian.views import diss, track, tuijian

urlpatterns = [
    path('track', track.track),
    path('track/diss', diss.track_diss),
    path('track/diss_theme', diss.track_diss_theme),
    path('diss/list', diss.diss_list),
    path('diss/theme_list', diss.diss_theme_list),
    path('cids_by_uid', tuijian.cids_by_uid),
    path('jian_history', tuijian.jian_history),
]
