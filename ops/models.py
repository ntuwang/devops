from django.db import models
from user.models import Users
from asset.models import ServerAsset

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


class Deploys(models.Model):
    BRANCH_LIST = (
        ('master', 'master'),
        ('bugfix', 'bugfix'),
        ('dev', 'dev')
    )
    JENKINS_YN = (
        ('yes', u'构建'),
        ('no', u'不构建'),
    )
    STATUS_LIST = (
        (0, '失败'),
        (1, '成功'),
        (2, '进行中'),
        (3, '等待'),
        (4, '回滚成功'),
        (5, '回滚失败'),
    )
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, verbose_name='发布项目',on_delete=models.CASCADE)
    host = models.ForeignKey(ServerAsset, blank=True, null=True, verbose_name='目标主机',on_delete=models.CASCADE)
    packs = models.CharField(max_length=100, blank=True, null=True, verbose_name='代码包')
    pack_url = models.CharField(max_length=100, blank=True, null=True, verbose_name='代码包路径')
    branch = models.CharField(max_length=100, blank=True, null=True, choices=BRANCH_LIST, verbose_name='Git分支')
    jenkinsbd = models.CharField(max_length=10, blank=True, null=True, choices=JENKINS_YN, verbose_name='Jenkins任务')
    progress = models.IntegerField(default=0, verbose_name='进度')
    status = models.IntegerField(default=0, choices=STATUS_LIST, verbose_name='状态')
    comment = models.TextField(blank=True, null=True, verbose_name='评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')

    def __unicode__(self):
        return self.project
