#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 17:27
# @Author  : 陈章

from datetime import datetime, timedelta
from typing import Dict
from typing import List

from django.db import models


class ContentsTag(models.Model):
    """
    内容标签表
    """
    content_id = models.IntegerField()
    tag_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'contents_tag'
        verbose_name = '内容标题对应表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'content_id={self.content_id}, tag_id={self.tag_id}'

    @classmethod
    def get_tids_by_cid(cls, cid):
        """
        根据内容id获取所有标签id
        :param cid:
        :return:
        """
        tids = cls.objects.filter(content_id=cid).values('tag_id')
        tids = [t['tag_id'] for t in tids]
        return tids

    @classmethod
    def get_limit_cids(cls, tid, all_jianed_cids, all_diss_cids, limit: int):
        """
        获取（指定标签的）没看过的 不是不喜欢的 指定条数内容
        :param tid:
        :param all_jianed_cids:
        :param all_diss_cids:
        :param limit:
        :return:
        """
        cids = cls.objects.all().distinct().order_by('?')
        if tid:
            cids = cids.filter(tag_id=tid)
        if all_jianed_cids:
            cids = cids.exclude(content_id__in=all_jianed_cids)
        if all_diss_cids:
            cids = cids.exclude(content_id__in=all_diss_cids)
        cids = cids.values('content_id')[:limit]
        cids = [c['content_id'] for c in cids]
        return cids


class Theme(models.Model):
    id = models.IntegerField(primary_key=True)
    platform = models.CharField(max_length=10)
    platform_type = models.IntegerField()
    keyword = models.CharField(max_length=200)
    keyword_type = models.CharField(max_length=20)
    href = models.CharField(max_length=500)
    name = models.CharField(max_length=255)
    desp = models.CharField(max_length=255)
    fans = models.IntegerField()
    image = models.CharField(max_length=100)
    theme_refter_type = models.IntegerField()
    creator = models.CharField(max_length=20)
    status = models.IntegerField()
    is_sift = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    sourceinfo = models.TextField(db_column='sourceInfo')  # Field name made lowercase.
    is_square = models.IntegerField()
    is_red_packet = models.IntegerField()
    sort = models.IntegerField()
    user_id = models.IntegerField()
    is_secret = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'theme'
        verbose_name = '主题表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'id={self.id}, name={self.name}'


class Contents(models.Model):
    """
    内容表
    """
    id = models.IntegerField(primary_key=True)
    theme = models.ForeignKey(Theme, on_delete=models.DO_NOTHING, related_name='theme')
    thirdparty_id = models.CharField(max_length=150, blank=True, null=True)
    publish_time = models.DateTimeField(blank=True, null=True)
    title = models.TextField()
    desp = models.TextField()
    contents_refter_type = models.IntegerField()
    media_type = models.IntegerField()
    pic_link = models.CharField(max_length=240)
    likes_count = models.IntegerField()
    comment_count = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    mongo_id = models.CharField(max_length=100)
    is_placed = models.IntegerField()
    is_secret = models.IntegerField()
    dynamic_time = models.DateTimeField()
    user_id = models.IntegerField()

    def __str__(self):
        return f'id={self.id}, title={self.title}'

    class Meta:
        managed = False
        db_table = 'contents'
        ordering = ['-updated_at']
        verbose_name = '内容表'
        verbose_name_plural = verbose_name

    @classmethod
    def get_all_abmormal_cids(cls):
        cids = cls.objects.exclude(status=0, is_secret=0, theme__status=0, theme__is_secret=0).values('id')
        return [c['id'] for c in cids]

    @classmethod
    def get_contentstr_list(cls, cid=None, nocids=None) -> Dict:
        records = cls.objects.filter(status=0, theme__status=0)
        if cid:
            records = records.filter(id=cid)
        if nocids:
            records = records.exclude(id__in=nocids)
        records = records.values('id', 'title', 'desp')
        d = {r['id']: r['title'] + r['desp'] for r in records}
        return d

    @classmethod
    def get_recently_cids(cls, recent_days: int = 7, limit: int = 20, nocids: List[int] = None):
        """
        获取最近更新的内容
        :param recent_days:
        :param limit:
        :param nocids: 要排除的内容id
        :return:
        """
        recent = datetime.now() - timedelta(days=recent_days)
        if nocids is None:
            nocids = []
        records = cls.objects.filter(status=0, is_secret=0, theme__status=0, theme__is_secret=0)
        records = records.exclude(id__in=nocids).filter(updated_at__gte=recent).order_by('-updated_at').values('id')[
                  :limit]
        cid_sim_list = [(r.get('id'), 1 / limit) for r in records]
        return cid_sim_list
