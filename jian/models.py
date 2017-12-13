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
        tids = cls.objects.filter(content_id=cid).values('tag_id')
        tids = [t['tag_id'] for t in tids]
        return tids

    @classmethod
    def get_limit_cids(cls, tid, viewd_content_ids, limit: int):
        cids = cls.objects.all().order_by('updated_at').distinct()
        if tid:
            cids = cids.filter(tag_id=tid)
        if viewd_content_ids:
            cids = cids.exclude(content_id__in=viewd_content_ids)
        cids = cids.values('content_id')[:limit]
        cids = [c['content_id'] for c in cids]
        return cids
