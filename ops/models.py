from django.db import models
from user.models import Users
from asset.models import ServerAsset


class DnsRecords(models.Model):
    rr = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=5, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    ttl = models.IntegerField(blank=True, null=True)
    domainname = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.rr

    class Meta:
        default_permissions = ()
        permissions = (
            ('view_dns', u'查看DNS'),
            ('manage_dns', u'管理DNS')
        )
        ordering = ['-id']
        verbose_name = u'域名解析'
