#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='kan_index'),
    url(r'^data_analyze$', views.data_analyze, name='kan_data_analyze'),
]
