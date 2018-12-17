#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

from django import template
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from asset.models import SaltGroup, SaltHost

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

    return {'users_dict': users_dict, 'select_users_dict': select_users_dict}


register.inclusion_tag('tags/tag_users.html')(show_users)


def show_minions(aid, arg):
    '''
    获取用户组或Salt分组主机
    :param aid:
    :return:
    '''
    select_minions_dict = {}
    minions = {i['pk']: i['nodename'] for i in SaltHost.objects.filter(status=True).values('pk', 'nodename')}

    if aid and arg == 'user_group':
        select_minions_dict = {i['pk']: i['nodename'] for i in
                               SaltHost.objects.filter(user_group=aid).values('pk', 'nodename')}
    elif aid and arg == 'saltgroup':
        select_minions_dict = {i['pk']: i['nodename'] for i in
                               SaltGroup.objects.get(pk=aid).minions.values('pk', 'nodename')}

    for i in select_minions_dict:
        if i in minions:
            del minions[i]

    return {'minions': sorted(minions.items()), 'select_minions_dict': sorted(select_minions_dict.items())}


register.inclusion_tag('tags/tag_minions.html')(show_minions)
