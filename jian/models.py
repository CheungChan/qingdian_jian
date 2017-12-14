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
    def get_limit_cids(cls, tid, all_jianed_cids, limit: int):
        """
        获取（指定标签的）没看过的 指定条数内容
        :param tid:
        :param all_jianed_cids:
        :param limit:
        :return:
        """
        cids = cls.objects.all().distinct()
        if tid:
            cids = cids.filter(tag_id=tid)
        if all_jianed_cids:
            cids = cids.exclude(content_id__in=all_jianed_cids).order_by('updated_at')
        cids = cids.values('content_id')[:limit]
        cids = [c['content_id'] for c in cids]
        return cids
