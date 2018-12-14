from django.db import models
from user.models import Users


# Create your models here.
class Message(models.Model):
    user = models.ForeignKey(Users, blank=True, null=True, verbose_name=u'用户', on_delete=models.CASCADE)
    audit_time = models.DateTimeField(auto_now_add=True, verbose_name=u'时间')
    type = models.CharField(max_length=10, verbose_name=u'类型')
    action = models.CharField(max_length=20, verbose_name=u'动作')
    action_ip = models.CharField(max_length=15, verbose_name=u'用户IP')
    content = models.TextField(verbose_name=u'内容')

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_message", u"查看操作记录"),
            ("edit_message", u"管理操作记录"),
        )
        ordering = ['-audit_time']
        verbose_name = u'审计信息'
        verbose_name_plural = u'审计信息管理'
