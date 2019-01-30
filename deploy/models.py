from django.db import models
from user.models import Users
from asset.models import ServerAsset
# Create your models here.


class Projects(models.Model):

    name = models.CharField(max_length=50, blank=True, verbose_name=u'项目名称')
    jenkins_name = models.CharField(max_length=50, blank=True, verbose_name=u'Jenkins任务名称')
    version = models.CharField(max_length=100, blank=True, verbose_name=u'版本')
    target_path = models.CharField(max_length=100, blank=True, verbose_name=u'目标路径')
    deploy_path = models.CharField(max_length=100, blank=True, verbose_name=u'部署路径')
    before_deploy = models.CharField(max_length=100, blank=True, verbose_name=u'部署前脚本')
    after_deploy = models.CharField(max_length=100, blank=True, verbose_name=u'部署后脚本')
    remote_history_dir = models.CharField(max_length=200, blank=True, verbose_name=u'备份历史路径')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=u'创建时间')
    updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=u'更新时间')

    def __str__(self):
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

    jenkins_list = (
        ('yes', u'构建'),
        ('no', u'不构建'),
    )

    status_list = (
        (0, '等待审批'),
        (1, '等待执行'),
        (2, '执行中'),
        (3, '执行成功'),
        (4, '执行失败'),
        (5, '拒绝执行'),
    )

    user = models.ForeignKey(Users,on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, verbose_name='发布项目',on_delete=models.CASCADE)
    host = models.ForeignKey(ServerAsset, blank=True, null=True, verbose_name='目标主机',on_delete=models.CASCADE)
    jenkins_job = models.CharField(max_length=10, blank=True, null=True, choices=jenkins_list, verbose_name='Jenkins任务')
    progress = models.IntegerField(default=0, verbose_name='进度')
    status = models.IntegerField(default=0,choices=status_list, verbose_name='状态')
    comment = models.TextField(blank=True, null=True, verbose_name='记录')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')

    def __str__(self):
        return '{0} for {1}'.format(self.user.username,self.project.name)

    class Meta:
        default_permissions = ()
        permissions = (
            ('view_deploy', u'查看部署'),
            ('manage_deploy', u'管理部署')
        )
        ordering = ['-id']
        verbose_name = u'部署'
