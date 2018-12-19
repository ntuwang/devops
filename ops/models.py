from django.db import models
from user.models import Users

# Create your models here.


class Projects(models.Model):
    name = models.CharField(max_length=100, blank=True, verbose_name=u'项目名称')
    app_type = models.CharField(max_length=100, blank=True, verbose_name=u'web容器')
    jenkins_name = models.CharField(max_length=200, blank=True, verbose_name=u'Jenkins任务名称')
    dest_dir = models.CharField(max_length=200, blank=True, verbose_name=u'目标路径')
    packlist = models.CharField(max_length=200, blank=True, verbose_name=u'代码包')
    local_dir = models.CharField(max_length=200, blank=True, verbose_name=u'临时路径')
    remote_history_dir = models.CharField(max_length=200, blank=True, verbose_name=u'备份历史路径')
    before_deploy = models.TextField(blank=True, null=True, verbose_name=u'部署前命令')
    after_deploy = models.TextField(blank=True, null=True, verbose_name=u'部署后命令')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=u'创建时间')
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=u'更新时间')

    def __unicode__(self):
        return self.name

    class Meta:
        default_permissions = ()
        permissions = (
            ('view_project', u'查看项目'),
            ('edit_project', u'管理项目')
        )
        ordering = ['-id']
        verbose_name = u'项目'
        verbose_name_plural = u'项目管理'

