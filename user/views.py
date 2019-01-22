#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

import functools
import warnings

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth
# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
)

from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from django.conf import settings as djsettings
from message.models import Message

from user.models import Users
import json

from .forms import *


def UserIP(request):
    '''
    获取用户IP
    '''

    ip = ''
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip


@login_required
def index(request):
    data = {
        'page_name': '仪表盘'
    }
    return render(request, 'index.html', data)


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, redirect_field_name=REDIRECT_FIELD_NAME, authentication_form=AuthenticationForm):
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))
    if request.method == "POST":
        form = ''
        if 'login' in request.POST:
            form = authentication_form(request, data=request.POST)
            if form.is_valid():
                if form.get_user() and form.get_user().is_active:
                    # Ensure the user-originating redirection url is safe.
                    if not is_safe_url(url=redirect_to, host=request.get_host()):
                        redirect_to = resolve_url(djsettings.LOGIN_REDIRECT_URL)
                    auth_login(request, form.get_user())
                    Message.objects.create(type=u'用户登录', user=request.user, action=u'用户登录',
                                           action_ip=UserIP(request), content='用户登录 %s' % request.user)
                    return HttpResponseRedirect(redirect_to)
            else:
                username = request.POST.get('username')
                user = Users.objects.get(username=username)
                Message.objects.create(type=u'用户登录', user=user, action=u'用户登录',
                                       action_ip=UserIP(request),
                                       content=u'用户登录失败 %s' % request.POST.get('username'))

    else:
        form = authentication_form(request)
    data = {
        'form': form,
        'page_name': '用户登录'
    }
    return render(request, 'registration/login.html', data)


def logout(request, next_page=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Logs out the user and displays 'You are logged out' message.
    """
    Message.objects.create(type=u'用户退出', user=request.user, action=u'用户退出', action_ip=UserIP(request),
                           content='用户退出 %s' % request.user)

    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    if (redirect_field_name in request.POST or
            redirect_field_name in request.GET):
        next_page = request.POST.get(redirect_field_name,
                                     request.GET.get(redirect_field_name))
        # Security check -- don't allow redirection to a different host.
        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        # Redirect to this page until the session has been cleared.
        return HttpResponseRedirect(next_page)
    return HttpResponseRedirect('/')


@login_required
def logoutw(request):
    return HttpResponseRedirect('/')


@login_required
def user_list(request):
    all_users = Users.objects.all()
    data = {
        'all_users': all_users,
        'page_name': '用户列表'
    }
    return render(request, 'user/user_list.html', data)


@login_required
def user_manage(request, aid=None, action=None):
    if request.user.has_perms(['asset.view_user', 'asset.edit_user']):
        page_name = ''
        if aid:
            user = get_object_or_404(Users, pk=aid)
            if action == 'edit':
                page_name = '编辑用户'
            if action == 'delete':
                user.delete()
                Message.objects.create(type=u'用户管理', user=request.user, action=u'删除用户', action_ip=UserIP(request),
                                       content=u'删除用户 %s%s，用户名 %s' % (user.last_name, user.first_name, user.username))
                return redirect('user_list')
        else:
            user = Users()
            action = 'add'
            page_name = '新增用户'

        if request.method == 'POST':
            form = UserForm(request.POST, instance=user)
            if form.is_valid():
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                perm_select = request.POST.getlist('perm_sel')
                perm_delete = request.POST.getlist('perm_del')
                if action == 'add' or action == 'edit':
                    form.save()
                    if password1 and password1 == password2:
                        user.set_password(password1)
                    user.save()
                    # 授予用户权限
                    user.user_permissions.add(*perm_select)
                    user.user_permissions.remove(*perm_delete)
                    Message.objects.create(type=u'用户管理', user=request.user, action=page_name, action_ip=UserIP(request),
                                           content=u'%s %s%s，用户名 %s' % (
                                               page_name, user.last_name, user.first_name, user.username))
                    return redirect('user_list')
        else:
            form = UserForm(instance=user)
        data = {
            'form': form,
            'page_name': page_name,
            'action': action,
            'aid': aid
        }

        return render(request, 'user/user_manage.html', data)
    else:
        raise Http404
