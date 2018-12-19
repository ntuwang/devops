#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao


from message.models import Message
from utils.saltapi import SaltApi
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.views import UserIP
from asset.forms import *
from asset.models import *
from saltstack.models import SaltHost,SaltGroup
from utils.config_parser import Conf_Parser
from asset.asset_info import MultipleCollect

try:
    import json
except ImportError:
    import simplejson as json


cps = Conf_Parser('conf/settings.conf')
sapi = SaltApi(url=cps.get('saltstack', 'url'), username=cps.get('saltstack', 'username'),
               password=cps.get('saltstack', 'password'))


@login_required
def get_server_asset_info(request):
    '''
    获取服务器资产信息
    '''

    if request.method == 'GET':
        if request.user.has_perm('asset.view_asset'):
            ret = ''
            all_server = ServerAsset.objects.all()
            if 'aid' in request.GET:
                aid = request.get_full_path().split('=')[1]
                server_detail = ServerAsset.objects.filter(id=aid)
                return render(request, 'asset/asset_server_detail.html', {'server_detail': server_detail})
            if 'action' in request.GET:
                if request.user.has_perm('asset.edit_asset'):
                    action = request.get_full_path().split('=')[1]
                    if action == 'flush':
                        q = SaltHost.objects.filter(alive=True)
                        tgt_list = []
                        [tgt_list.append(i.nodename) for i in q]
                        ret = MultipleCollect(tgt_list)
                        for i in ret:
                            try:
                                server_asset = get_object_or_404(ServerAsset, nodename=i['nodename'])
                                hostname = server_asset.hostname
                                for j in i:
                                    if i[j] != 'Nan':
                                        setattr(server_asset, j, i[j])
                                server_asset.hostname = hostname
                                server_asset.save()
                            except:
                                server_asset = ServerAsset()
                                for j in i:
                                    setattr(server_asset, j, i[j])
                                server_asset.save()
                        return redirect('server_info')
                else:
                    raise Http404

        else:
            raise Http404
        return render(request, 'asset/asset_server_list.html', {'all_server': all_server})

    if request.method == 'POST':
        if request.user.has_perm('asset.edit_asset'):
            field = request.POST.get('field')
            value = request.POST.get('value')
            value = str(value)
            id = request.POST.get('id')
            ServerAsset.objects.filter(id=id).update(**{field: value})
            return HttpResponse(value)
        else:
            raise Http404


@login_required
def cloud_asset_manage(request, aid=None, action=None):
    """
    Manage Cloud
    """
    if request.user.has_perms(['asset.view_asset', 'asset.edit_asset']):
        page_name = ''
        if aid:
            cloud_list = get_object_or_404(Clouds, pk=aid)
            if action == 'edit':
                page_name = '编辑云供应商'
            if action == 'delete':
                cloud_list.delete()
                return redirect('cloud_asset_list')
        else:
            cloud_list = Clouds()
            action = 'add'
            page_name = '新增云供应商'

        if request.method == 'POST':
            form = CloudsForm(request.POST, instance=cloud_list)

            if form.is_valid():
                if action == 'add':
                    form.save()
                    return redirect('cloud_asset_list')
                if action == 'edit':
                    form.save()
                    return redirect('cloud_asset_list')
        else:
            form = CloudsForm(instance=cloud_list)

        return render(request, 'asset/asset_cloud_manage.html',
                      {"form": form, "page_name": page_name, "action": action})
    else:
        raise Http404


@login_required
def cloud_asset_list(request):
    """
    cloud列表、cloud详细
    """
    if request.user.has_perm('asset.view_asset'):
        if request.method == 'GET':
            if 'aid' in request.GET:
                aid = request.get_full_path().split('=')[1]
                idc_detail = Clouds.objects.filter(id=aid)
                return render(request, 'asset/asset_cloud_detail.html', {'cloud_detail': idc_detail})

        all_cloud = Clouds.objects.all()

        return render(request, 'asset/asset_cloud_list.html', {'all_cloud_list': all_cloud})
    else:
        raise Http404


@login_required
def server_asset_manage(request, aid=None, action=None):
    """
    Manage Server
    """
    if request.user.has_perms(['asset.view_asset', 'asset.edit_asset']):
        page_name = ''
        if aid:
            server_list = get_object_or_404(ServerAsset, pk=aid)
            if action == 'edit':
                page_name = '编辑Server'
            if action == 'delete':
                server_list.delete()
                return redirect('server_info')
        else:
            server_list = ServerAsset()
            action = 'add'
            page_name = '新增Server'

        if request.method == 'POST':
            form = ServerAssetForm(request.POST, instance=server_list)
            if form.is_valid():
                if action == 'add':
                    form.save()
                    return redirect('server_info')
                if action == 'edit':
                    form.save()
                    return redirect('server_info')
        else:
            form = ServerAssetForm(instance=server_list)

        return render(request, 'asset/asset_server_manage.html',
                      {"form": form, "page_name": page_name, "action": action})
    else:
        raise Http404


@login_required
def owner_list(request):
    """
    az列表、az详细
    """
    if request.user.has_perm('asset.view_asset'):

        all_onwer = Owners.objects.all()

        return render(request, 'asset/asset_owner_list.html', {'all_onwer_list': all_onwer})
    else:
        raise Http404


@login_required
def owner_manage(request, aid=None, action=None):
    """
    Manage AZ
    """
    if request.user.has_perms(['asset.view_asset', 'asset.edit_asset']):
        page_name = ''
        if aid:
            owner_list = get_object_or_404(Owners, pk=aid)
            if action == 'edit':
                page_name = '编辑owner'
            if action == 'delete':
                owner_list.delete()
                return redirect('az_asset_list')
        else:
            owner_list = Owners()
            action = 'add'
            page_name = '新增owner'

        if request.method == 'POST':
            form = OwnerForms(request.POST, instance=owner_list)

            if form.is_valid():
                if action == 'add':
                    form.save()
                    return redirect('owner_list')
                if action == 'edit':
                    form.save()
                    return redirect('owner_list')
        else:
            form = OwnerForms(instance=owner_list)

        return render(request, 'asset/asset_owner_manage.html',
                      {"form": form, "page_name": page_name, "action": action})
    else:
        raise Http404

