#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao


from message.models import Message
from utils.saltapi import SaltAPI
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.views import UserIP
from asset.forms import *
from asset.models import *
from utils.config_parser import ConfParser

try:
    import json
except ImportError:
    import simplejson as json

import time
import datetime
import shutil
import os
import re
import tarfile, zipfile

from io import StringIO
import json

cps = ConfParser('devops/settings.conf')
sapi = SaltAPI(url=cps.get('saltstack', 'url'), username=cps.get('saltstack', 'username'),
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


@login_required
def salt_key_list(request):
    '''
    salt主机列表
    '''

    if request.user.is_superuser:
        minions = SaltHost.objects.filter(status=True)
        minions_pre = SaltHost.objects.filter(status=False)
        return render(request, 'asset/salt_key_list.html', {'all_minions': minions, 'all_minions_pre': minions_pre})
    else:
        raise Http404


@login_required
def salt_key_import(request):
    '''
    导入salt主机
    '''
    if request.user.is_superuser:
        minions, minions_pre = sapi.list_all_key()
        alive = False
        ret_alive = sapi.salt_alive('*')
        for node_name in minions:
            try:
                alive = ret_alive[node_name]
                alive = True
            except:
                alive = False
            try:
                SaltHost.objects.create(hostname=node_name, alive=alive, status=True)
            except:
                salthost = SaltHost.objects.get(hostname=node_name)
                now = datetime.datetime.now()
                alive_old = SaltHost.objects.get(hostname=node_name).alive
                if alive != alive_old:
                    salthost.alive_time_last = now
                    salthost.alive = alive
                salthost.alive_time_now = now
                salthost.save()
        for node_name in minions_pre:
            try:
                SaltHost.objects.get_or_create(hostname=node_name, alive=alive, status=False)
            except:
                print('not create')

        return redirect('key_list')
    else:
        raise Http404


@login_required
def salt_key_manage(request, hostname=None):
    '''
    接受或拒绝salt主机，同时更新数据库
    '''
    if request.user.is_superuser:
        if request.method == 'GET':
            hostname = request.GET.get('hostname')
            salthost = SaltHost.objects.get(hostname=hostname)
            action = ''

            if request.GET.has_key('add'):
                ret = sapi.accept_key(hostname)
                if ret:
                    salthost.status = True
                    salthost.save()
                    result = 3
                    action = u'添加主机'
            if request.GET.has_key('delete'):
                ret = sapi.delete_key(hostname)
                if ret:
                    salthost.status = False
                    salthost.save()
                    result = 2
                    action = u'删除主机'
            if request.GET.has_key('flush') and request.is_ajax():
                # result: 0 在线 | 1 离线
                result = 0
                ret = sapi.salt_alive(hostname)
                try:
                    alive = ret[hostname]
                    alive = True
                except:
                    alive = False
                    result = 1
                salthost.alive = alive
                salthost.save()
                action = u'刷新主机'
                if action:
                    Message.objects.create(type=u'部署管理', user=request.user.first_name, action=action,
                                           action_ip=UserIP(request),
                                           content=u'%s %s' % (action, salthost.hostname))
                return HttpResponse(json.dumps(result))

            if action:
                Message.objects.create(type=u'部署管理', user=request.user.first_name, action=action,
                                       action_ip=UserIP(request), content=u'%s %s' % (action, salthost.hostname))

        return redirect('key_list')
    else:
        raise Http404


@login_required
def salt_group_list(request):
    '''
    salt主机分组列表
    '''

    if request.user.is_superuser:
        groups = SaltGroup.objects.all()
        return render(request, 'salt_group_list.html', {'all_groups': groups})
    else:
        raise Http404


@login_required
def salt_group_manage(request, id=None):
    '''
    salt主机分组管理，同时更新salt-master配置文件
    '''
    if request.user.is_superuser:
        action = ''
        page_name = ''
        if id:
            group = get_object_or_404(SaltGroup, pk=id)
            action = 'edit'
            page_name = '编辑分组'
        else:
            group = SaltGroup()
            action = 'add'
            page_name = '新增分组'

        if request.method == 'GET':
            if request.GET.has_key('delete'):
                id = request.GET.get('id')
                group = get_object_or_404(SaltGroup, pk=id)
                group.delete()
                Message.objects.create(type=u'部署管理', user=request.user.first_name, action=u'删除分组',
                                       action_ip=UserIP(request), content='删除分组 %s' % group.nickname)
                with open('./saltconfig/nodegroup.conf', 'r') as f:
                    with open('./nodegroup', 'w') as g:
                        for line in f.readlines():
                            if group.groupname not in line:
                                g.write(line)
                shutil.move('./nodegroup', './saltconfig/nodegroup.conf')
                return redirect('group_list')

        if request.method == 'POST':
            form = SaltGroupForm(request.POST, instance=group)
            if form.is_valid():
                minion_select = request.POST.getlist('minion_sel')
                minion_delete = request.POST.getlist('minion_del')
                # 前台分组以别名显示，组名不变
                if action == 'add':
                    group = form.save(commit=False)
                    group.groupname = form.cleaned_data['nickname']
                elif action == 'edit':
                    form.save()
                group.save()
                group.minions.add(*minion_select)
                group.minions.remove(*minion_delete)
                group.save()
                Message.objects.create(type=u'部署管理', user=request.user.first_name, action=page_name,
                                       action_ip=UserIP(request), content='%s %s' % (page_name, group.nickname))

                minions_l = []
                for m in group.minions.values('hostname'):
                    minions_l.append(m['hostname'])
                minions_str = ','.join(minions_l)
                try:
                    with open('./saltconfig/nodegroup.conf', 'r') as f:
                        with open('./nodegroup', 'w') as g:
                            for line in f.readlines():
                                if group.groupname not in line:
                                    g.write(line)
                            g.write("  %s: 'L@%s'\n" % (group.groupname, minions_str))
                    shutil.move('./nodegroup', './saltconfig/nodegroup.conf')
                except:
                    with open('./saltconfig/nodegroup.conf', 'w') as g:
                        g.write("nodegroups:\n  %s: 'L@%s'\n" % (group.groupname, minions_str))

                import subprocess
                subprocess.Popen('systemctl restart salt-master salt-api', shell=True)
                return redirect('group_list')
        else:
            form = SaltGroupForm(instance=group)

        return render(request, 'salt_group_manage.html',
                      {'form': form, 'action': action, 'page_name': page_name, 'aid': id})
    else:
        raise Http404


@login_required
def salt_module_list(request):
    '''
    模块列表
    '''
    if request.user.has_perm('deploy.view_deploy'):
        if request.user.is_superuser:
            module_list = ModuleUpload.objects.all()
        else:
            # 获取用户创建或公开模块
            module_visible_list = [{'pk': i.pk, 'name': i.name, 'module': i.module, 'remark': i.remark, 'user': i.user}
                                   for i in ModuleUpload.objects.filter(Q(user=request.user) | Q(visible=2))]
            # 获取用户组模块
            module_user_group_list = [
                {'pk': i.pk, 'name': i.name, 'module': i.module, 'remark': i.remark, 'user': i.user}
                for g in Users.objects.get(pk=request.user.pk).group.all() for i in
                ModuleUpload.objects.filter(user_group=g)]
            # 合并list
            module_list = module_visible_list + [i for i in module_user_group_list if i not in module_visible_list]
        return render(request, 'salt_module_list.html', {'modules': module_list})
    else:
        raise Http404


@login_required
def salt_module_manage(request, id=None):
    '''
    模块管理
    '''
    if request.user.has_perms(['deploy.view_deploy', 'deploy.edit_module']):
        ret = ''
        upload_stat = True
        if id:
            module = get_object_or_404(ModuleUpload, pk=id)
            if request.user.pk != module.user.pk and not request.user.is_superuser:
                return HttpResponse("Not Allowed!")
            old_path = module.upload_path.path.split('.')
            action = 'edit'
            page_name = '编辑模块'
        else:
            module = ModuleUpload()
            action = 'add'
            page_name = '新增模块'

        if request.method == 'GET':
            if request.GET.has_key('delete'):
                id = request.GET.get('id')
                module = get_object_or_404(ModuleUpload, pk=id)
                if request.user.pk != module.user.pk and not request.user.is_superuser:
                    return HttpResponse("Not Allowed!")
                module.delete()
                Message.objects.create(type=u'部署管理', user=request.user.first_name, action=u'删除模块',
                                       action_ip=UserIP(request), content=u'删除模块 %s' % module.name)
                cur_path = module.upload_path.path.split('.')[0]
                try:
                    os.remove('%s.sls' % (cur_path))
                except:
                    shutil.rmtree(cur_path, ignore_errors=True)
                return redirect('module_list')

        if request.method == 'POST':
            form = ModuleForm(request.POST, request.FILES, instance=module)
            if form.is_valid():
                visible = form.cleaned_data['visible']
                module_list = form.cleaned_data['module'].split('.')
                user_group = request.POST.get('user_group')

                if visible == 0:
                    ext_path = './media/salt/module/user_%s' % request.user.id
                    salt_path = 'salt://module/user_%s/%s' % (request.user.id, module_list[0])
                elif visible == 2:
                    ext_path = './media/salt/module/public'
                    salt_path = 'salt://module/public/%s' % module_list[0]
                else:
                    ext_path = './media/salt/module/group_%s' % user_group
                    salt_path = 'salt://module/group_%s/%s' % (user_group, module_list[0])
                file_exists = request.POST.get('upload_path')
                file_name = form.cleaned_data['upload_path']
                file_ext = str(file_name).split('.')[-1]
                ext = ['bz2', 'gz', 'zip', 'sls']
                if file_ext in ext:
                    if action == 'add':
                        module = form.save(commit=False)
                        module.user = request.user
                    else:
                        form.save()
                    module.save()

                    Message.objects.create(type=u'部署管理', user=request.user.first_name, action=page_name,
                                           action_ip=UserIP(request), content='%s %s' % (page_name, module.name))

                    src = module.upload_path.path

                    if file_exists == None:
                        try:
                            os.remove('%s.sls' % old_path[0])
                        except:
                            pass
                        try:
                            if file_ext == 'zip':
                                tar = zipfile.ZipFile(src)
                            else:
                                tar = tarfile.open(src)

                            tar.extractall(path=ext_path)
                            tar.close()
                            with open('%s/%s/%s.sls' % (ext_path, module_list[0], module_list[1]), 'r+') as f:
                                t = f.read()
                                t = t.replace('SALTSRC', salt_path)
                                f.seek(0, 0)
                                f.write(t)
                            ret = u'模块 %s 已上传完成！' % (file_name)
                        except:
                            upload_stat = False
                            ret = u'模块 %s 上传失败，请上传.sls文件或.tar.gz/.tar.bz2/.zip压缩包并确认压缩文件是否损坏！' % (file_name)
                        try:
                            os.remove(src)
                        except:
                            shutil.rmtree(src, ignore_errors=True)
                            pass

                    if upload_stat:
                        return redirect('module_list')
                    else:
                        return render(request, 'salt_module_manage.html',
                                      {'form': form, 'action': action, 'page_name': page_name, 'ret': ret})
                else:
                    ret = u'不支持的文件格式，请上传.sls文件或.tar.gz/.tar.bz2/.zip压缩包！'
        else:
            form = ModuleForm(instance=module)
        return render(request, 'salt_module_manage.html',
                      {'form': form, 'action': action, 'page_name': page_name, 'ret': ret, 'id': id})
    else:
        raise Http404


@login_required
def salt_ajax_minions(request):
    '''
    获取不同分组下的主机列表
    '''
    if request.user.has_perms(['deploy.view_deploy']):
        ret = []
        if request.method == 'POST':
            grp = request.POST.get('tgt_select', None)
            tgt_select = SaltGroup.objects.get(nickname=grp).groupname
            if request.is_ajax():
                group = SaltGroup.objects.get(groupname=tgt_select)
                group_minions = group.minions.all()
                for i in group_minions:
                    ret.append(i.hostname)

                return HttpResponse(json.dumps(ret))
    else:
        raise Http404
