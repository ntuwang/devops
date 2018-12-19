from message.models import Message
from utils.saltapi import SaltApi
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from user.views import UserIP
from saltstack.forms import *
from saltstack.models import *
from utils.config_parser import Conf_Parser


try:
    import json
except ImportError:
    import simplejson as json
import datetime
import shutil


cps = Conf_Parser('conf/settings.conf')
sapi = SaltApi(url=cps.get('saltstack', 'url'), username=cps.get('saltstack', 'username'),
               password=cps.get('saltstack', 'password'))

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
                SaltHost.objects.create(nodename=node_name, alive=alive, status=True)
            except:
                salthost = SaltHost.objects.get(nodename=node_name)
                now = datetime.datetime.now()
                alive_old = SaltHost.objects.get(nodename=node_name).alive
                if alive != alive_old:
                    salthost.alive_time_last = now
                    salthost.alive = alive
                salthost.alive_time_now = now
                salthost.save()
        for node_name in minions_pre:
            try:
                SaltHost.objects.get_or_create(nodename=node_name, alive=alive, status=False)
            except:
                print('not create')

        return redirect('salt_key_list')
    else:
        raise Http404


@login_required
def salt_key_manage(request, nodename=None):
    '''
    接受或拒绝salt主机，同时更新数据库
    '''
    if request.user.is_superuser:
        if request.method == 'GET':
            nodename = request.GET.get('nodename')
            salthost = SaltHost.objects.get(nodename=nodename)
            action = ''

            if 'add' in request.GET:
                ret = sapi.accept_key(nodename)
                if ret:
                    salthost.status = True
                    salthost.save()
                    result = 3
                    action = u'添加主机'
            if 'delete' in request.GET:
                ret = sapi.delete_key(nodename)
                if ret:
                    salthost.status = False
                    salthost.save()
                    result = 2
                    action = u'删除主机'
            if 'flush' in request.GET and request.is_ajax():
                # result: 0 在线 | 1 离线
                result = 0
                ret = sapi.salt_alive(nodename)
                try:
                    alive = ret[nodename]
                    alive = True
                except:
                    alive = False
                    result = 1
                salthost.alive = alive
                salthost.save()
                action = u'刷新主机'
                if action:
                    Message.objects.create(type=u'部署管理', user=request.user, action=action,
                                           action_ip=UserIP(request),
                                           content=u'%s %s' % (action, salthost.nodename))
                return HttpResponse(json.dumps(result))

            if action:
                Message.objects.create(type=u'部署管理', user=request.user, action=action,
                                       action_ip=UserIP(request), content=u'%s %s' % (action, salthost.nodename))

        return redirect('salt_key_list')
    else:
        raise Http404


@login_required
def salt_group_list(request):
    '''
    salt主机分组列表
    '''

    if request.user.is_superuser:
        groups = SaltGroup.objects.all()
        return render(request, 'asset/salt_group_list.html', {'all_groups': groups})
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
            if 'delete' in request.GET:
                id = request.GET.get('id')
                group = get_object_or_404(SaltGroup, pk=id)
                group.delete()
                Message.objects.create(type=u'部署管理', user=request.user, action=u'删除分组',
                                       action_ip=UserIP(request), content='删除分组 %s' % group.nickname)
                with open('./saltconfig/nodegroup.conf', 'r') as f:
                    with open('./nodegroup', 'w') as g:
                        for line in f.readlines():
                            if group.groupname not in line:
                                g.write(line)
                shutil.move('./nodegroup', './saltconfig/nodegroup.conf')
                return redirect('salt_group_list')

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
                Message.objects.create(type=u'部署管理', user=request.user, action=page_name,
                                       action_ip=UserIP(request), content='%s %s' % (page_name, group.nickname))

                minions_l = []
                for m in group.minions.values('nodename'):
                    minions_l.append(m['nodename'])
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
                    with open('conf/saltconfig/nodegroup.conf', 'w') as g:
                        g.write("nodegroups:\n  %s: 'L@%s'\n" % (group.groupname, minions_str))

                return redirect('salt_group_list')
        else:
            form = SaltGroupForm(instance=group)

        return render(request, 'asset/salt_group_manage.html',
                      {'form': form, 'action': action, 'page_name': page_name, 'aid': id})
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
                    ret.append(i.nodename)

                return HttpResponse(json.dumps(ret))
    else:
        raise Http404



@login_required
def salt_task_list(request):
    '''
    任务列表
    '''
    if request.user.has_perm('userperm.view_message'):
        if request.method == 'GET':
            if request.GET.has_key('tid'):
                tid = request.get_full_path().split('=')[1]
                log_detail = Message.objects.filter(user=request.user.first_name).filter(id=tid).exclude(
                    type=u'用户登录').exclude(type=u'用户退出')
                return render(request, 'saltstack/salt_task_detail.html', {'log_detail': log_detail})

        logs = Message.objects.filter(user=request.user.first_name).exclude(type=u'用户登录').exclude(type=u'用户退出')[:200]

        return render(request, 'saltstack/salt_task_list.html', {'all_logs': logs})
    else:
        raise Http404


@login_required
def salt_task_check(request):
    '''
    任务查询
    '''
    return render(request, 'saltstack/salt_task_check.html', {})


@login_required
def salt_task_running(request):
    '''
    获取运行中的任务
    '''
    ret = []
    if request.method == 'POST':
        if request.user.has_perms(['userperm.view_message', 'deploy.edit_deploy']):
            if request.is_ajax():
                rst = sapi.salt_running_jobs()
                for k, v in rst.items():
                    dict = {}
                    dict['jid'] = k
                    dict['func'] = v['Function']
                    dict['tgt_type'] = v['Target-type']
                    dict['running'] = v['Arguments'][0].replace(';echo ":::"$?', '')
                    str_tgt = ''
                    for i in v['Running']:
                        for m, n in i.items():
                            str_tgt = str_tgt + m + ':' + str(n) + '<br />'
                    dict['tgt_pid'] = str_tgt
                    ret.append(dict)
                return HttpResponse(json.dumps(ret))
    if request.GET.has_key('delete'):
        jid = request.GET.get('jid')
        import subprocess
        p = subprocess.Popen("salt '*' saltutil.term_job %s" % jid, shell=True, stdout=subprocess.PIPE)
        out = p.stdout.readlines()
        return HttpResponse(json.dumps('Job %s killed.' % jid))

    return render(request, 'saltstack/salt_task_running_list.html', {})
