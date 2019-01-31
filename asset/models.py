#!/usr/bin/env python

from django.db import models
from user.models import Users
import random


def user_dir_path(instance, filename):
    if instance.visible == 0:
        return 'salt/module/user_{user_id}/{filename}'.format(user_id=instance.user.id, filename=filename)
    elif instance.visible == 2:
        return 'salt/module/public/{filename}'.format(filename=filename)
    else:
        return 'salt/module/group_{group_id}/{filename}'.format(group_id=instance.user_group.id, filename=filename)


def file_upload_dir_path(instance, filename):
    return 'salt/fileupload/user_{user_id}/{file_tag}/{filename}'.format(
        user_id=instance.user.id, file_tag=instance.file_tag, filename=filename)


class Clouds(models.Model):
    Provider = (
        (str(1), u"aws"),
        (str(2), u"aliyun"),
        (str(1), u"azure"),
        (str(2), u"tecent"),
    )

    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'区域名称')
    region_id = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'区域ID')
    provider = models.CharField(max_length=255, null=True, blank=True, choices=Provider, verbose_name=u'供应商')
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name=u'描述信息')

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = ()
        verbose_name_plural = u'云管理'


class Owners(models.Model):
    name = models.CharField(u"负责人姓名", max_length=50, unique=True, null=False, blank=False)
    phone = models.CharField(u"负责人手机", max_length=50, null=False, blank=False)
    email = models.CharField(u"负责人邮箱", max_length=100, null=True, blank=True)
    weChat = models.CharField(u"负责人微信", max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        default_permissions = ()
        verbose_name_plural = u'联系人管理'


# 系统登录用户
class AssetLoginUser(models.Model):
    username = models.CharField(max_length=64, verbose_name="用户名", default='root', null=True, blank=True)
    password = models.CharField(max_length=256, blank=True, null=True, verbose_name='密码')
    private_key = models.FileField(upload_to='upload/privatekey/%Y%m%d{}'.format(random.randint(0, 99999)),
                                   verbose_name="私钥", null=True, blank=True)

    ps = models.CharField(max_length=10240, verbose_name="备注", null=True, blank=True)
    ctime = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间', blank=True)
    utime = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间', blank=True)

    class Meta:
        db_table = "AssetLoginUser"
        verbose_name = "资产用户"
        verbose_name_plural = '资产用户'

    def __str__(self):
        return self.username


# Create your models here.
class ServerAsset(models.Model):
    nodename = models.CharField(max_length=50, unique=True, blank=True, null=True, default=None, verbose_name=u'Salt主机')
    hostname = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name=u'主机名')
    private_ip = models.GenericIPAddressField(max_length=15, blank=True, null=True, verbose_name=u"内网IP")
    public_ip = models.GenericIPAddressField(max_length=15, blank=True, null=True, verbose_name=u"外网IP")
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'规格')
    status = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'状态')
    manufacturer = models.CharField(max_length=50, blank=True, verbose_name=u'厂商')
    productname = models.CharField(max_length=100, blank=True, verbose_name=u'型号')
    sn = models.CharField(max_length=50, blank=True, verbose_name=u'序列号')
    cpu_model = models.CharField(max_length=100, default=None, null=True, verbose_name=u'CPU型号')
    cpu_nums = models.PositiveSmallIntegerField(default=None, null=True, verbose_name=u'CPU线程')
    memory = models.CharField(max_length=20, default=None, blank=True, null=True, verbose_name=u'内存')
    disk = models.TextField(blank=True, verbose_name=u'硬盘')
    network = models.TextField(blank=True, verbose_name=u'网络接口')
    os = models.CharField(max_length=200, blank=True, verbose_name=u'操作系统')
    virtual = models.CharField(max_length=20, blank=True, verbose_name=u'虚拟化')
    kernel = models.CharField(max_length=200, blank=True, verbose_name=u'内核')
    shell = models.CharField(max_length=10, blank=True, verbose_name=u'Shell')
    zmqversion = models.CharField(max_length=10, blank=True, verbose_name=u'ZeroMQ')
    saltversion = models.CharField(max_length=10, blank=True, verbose_name=u'Salt版本')
    locale = models.CharField(max_length=200, blank=True, verbose_name=u'编码')
    selinux = models.CharField(max_length=50, blank=True, verbose_name=u'Selinux')
    idc = models.CharField(max_length=50, blank=True, verbose_name=u'机房')
    region = models.ForeignKey(Clouds, blank=True, null=True, verbose_name=u'所在区', on_delete=models.CASCADE)
    owner = models.ForeignKey(Owners, blank=True, null=True, verbose_name=u'负责人', on_delete=models.CASCADE)
    user = models.ForeignKey(AssetLoginUser, blank=True, null=True, verbose_name=u'资产登录用户', on_delete=models.CASCADE)

    def __str__(self):
        return self.hostname

    class Meta:
        default_permissions = ()
        permissions = (
            ("view_asset", u"查看资产"),
            ("edit_asset", u"管理资产"),
        )
        verbose_name = u'主机资产信息'
        verbose_name_plural = u'主机资产信息管理'

