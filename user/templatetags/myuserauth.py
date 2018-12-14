#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

from django import template
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from user.models import Users

register = template.Library()

def show_users(aid, value):
    '''
    获取用户
    '''

    select_users_dict = {}
    users_dict = {i['pk']: i['first_name'] for i in Users.objects.values('pk', 'first_name')}

    for i in select_users_dict:
        if i in users_dict:
            del users_dict[i]

    return {'users_dict':users_dict, 'select_users_dict':select_users_dict}

register.inclusion_tag('user/tag_users.html')(show_users)
