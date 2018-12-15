#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

from django import template
from django.db.models import Q

register = template.Library()


def show_groups(pk, user_type):
    '''
    远程命令、模块部署及文件管理中显示所有分组
    '''
    group_dict = {}
    if user_type:
        group_dict = {i['groupname']:i['nickname'] for i in SaltGroup.objects.values('groupname', 'nickname')}
    else:
        d = User.objects.get(pk=pk).department
        group_dict = {i['groupname']:i['nickname'] for d in User.objects.get(pk=pk).department.all()
                      for i in d.saltgroup_department_set.values('groupname', 'nickname')}

    return {'group_dict':sorted(list(set(group_dict.items())))}

register.inclusion_tag('tag_user_departments.html')(show_groups)