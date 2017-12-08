from django.db import models


class Contents(models.Model):
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


class ContentsTag(models.Model):
    content = models.ForeignKey(Contents, models.DO_NOTHING)
    tag_id = models.IntegerField()
    name = models.CharField(max_length=10)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'contents_tag'

    @classmethod
    def get_tags_by_content_pk(cls, cid):
        tags = cls.objects.filter(content__pk=cid).values('tag_id')
        tags = [t['tag_id'] for t in tags]
        return tags
