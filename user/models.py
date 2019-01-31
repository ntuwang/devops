from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
from django.core.validators import RegexValidator


class Users(AbstractUser):
    USER_ROLE_CHOICES = (
        ('SU', u'超级管理员'),
        ('GA', u'组管理员'),
        ('CU', u'普通用户')
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': ("A user with that username already exists."),
        },
        verbose_name=u'用户名',
    )
    mobile = models.CharField(max_length=30, blank=True, verbose_name=u'联系电话', validators=[
        RegexValidator(regex='^[^0]\d{6,7}$|^[1]\d{10}$', message=u'请输入正确的电话或手机号码', code=u'号码错误')],
                              error_messages={'required': u'联系电话不能为空'})
    position = models.CharField(max_length=20, blank=True, verbose_name=u'职位')
    role = models.CharField(max_length=2, choices=USER_ROLE_CHOICES, default='CU')

    def __str__(self):
        return self.username


class UserCommand(models.Model):
    name = models.CharField(
        max_length=80,
        unique=True,
        verbose_name=u'命令别名')
    command = models.TextField(blank=True, verbose_name=u'系统命令')
    is_allow = models.BooleanField(default=True, verbose_name=u'状态')

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = ()
        permissions = (
            ("edit_remote_permission", u"管理远程权限"),
        )
        verbose_name = u'远程命令'
        verbose_name_plural = u'远程命令管理'


class UserDirectory(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=u'目录别名')
    directory = models.TextField(blank=True, verbose_name=u'系统目录')
    is_allow = models.BooleanField(default=True, verbose_name=u'状态')

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = ()
        verbose_name = u'远程目录'
        verbose_name_plural = u'远程目录管理'


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
