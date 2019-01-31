from django.db import models
from asset.models import AssetLoginUser

# Create your models here.


class DBInfo(models.Model):

    STATUS_LIST = (
        (0, 'online'),
        (1, 'offline')
    )
    db_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='DB名称')
    db_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='实例IP')
    db_port = models.IntegerField(default=3306, verbose_name='实例端口')
    status = models.IntegerField(default=0, choices=STATUS_LIST, verbose_name='实例状态')
    comment = models.TextField(blank=True, null=True, verbose_name='描述')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    utime = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')
    user = models.ForeignKey(AssetLoginUser, blank=True, null=True, verbose_name=u'登录用户', on_delete=models.CASCADE)

    def __str__(self):
        return self.db_name

    class Meta:
        ordering = ['-id']
        verbose_name = u'数据库'
        verbose_name_plural = u'DB管理'
        permissions = (
            ('view_db', u'查看DB'),
            ('manage_db', u'管理DB')
        )