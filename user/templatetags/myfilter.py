#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

from django import template
from django.contrib.auth.models import Group
from user.models import Users
from django.db.models import Q
from django.shortcuts import get_object_or_404

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg, 'required':'required'})

@register.filter(name='group_minions')
def minions(value):
    '''
    分组列表中显示所有主机
    '''

    try:
        group_minions = value.minions.all()
        return group_minions
    except:
        return ''

@register.filter(name='group_users')
def all_users(group):
    '''
    分组列表中显示所有主机
    '''

    try:
        #all_users = group.user_set.all()
        all_users = Users.objects.filter(group=group)
        return all_users
    except:
        return ''

@register.filter(name='is_super')
def user_is_super(pk):
    '''
    是否为超级用户
    '''
    if pk:
        return Users.objects.get(pk=pk).is_superuser
    else:
        return None