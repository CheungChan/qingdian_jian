from typing import Dict
from django.db import models


class ContentsTag(models.Model):
    content_id = models.IntegerField()
    tag_id = models.IntegerField()
    name = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'contents_tag'

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


class Contents(models.Model):
    id = models.IntegerField(primary_key=True)
    theme_id = models.IntegerField()
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

    class Meta:
        managed = False
        db_table = 'contents'

    @classmethod
    def get_contentstr_list(cls, cid=None, nocids=None) -> Dict:
        records = cls.objects.all()
        if cid:
            records = records.filter(id=cid)
        if nocids:
            records = records.exclude(id__in=nocids)
        records = records.values('id', 'title', 'desp')
        d = {r['id']: r['title'] + r['desp'] for r in records}
        return d
