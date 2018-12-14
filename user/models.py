from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, PermissionsMixin
from django.core.validators import RegexValidator


class Users(AbstractUser):
    USER_ROLE_CHOICES = (
        ('SU', u'超级管理员'),
        ('GA', u'组管理员'),
        ('CU', u'普通用户')
    )

    mobile = models.CharField(max_length=30, blank=True, verbose_name=u'联系电话', validators=[
        RegexValidator(regex='^[^0]\d{6,7}$|^[1]\d{10}$', message=u'请输入正确的电话或手机号码', code=u'号码错误')],
                              error_messages={'required': u'联系电话不能为空'})
    position = models.CharField(max_length=20, blank=True, verbose_name=u'职位')
    role = models.CharField(max_length=2, choices=USER_ROLE_CHOICES, default='CU')

    def __str__(self):
        return self.username
