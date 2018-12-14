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

from user.models import Users
import json

from .forms import *


@login_required
def index(request):
    return render(request, 'index.html', {})


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

    else:
        form = authentication_form(request)
    return render(request, 'registration/login.html', {'form': form, 'title': '用户登录'})


def logout(request, next_page=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Logs out the user and displays 'You are logged out' message.
    """
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
    auth.logout(request)
    return HttpResponseRedirect('/')
