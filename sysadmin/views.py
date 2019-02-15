from user.models import Message
from utils.saltapi import SaltApi

from user.views import UserIP
from sysadmin.forms import SaltFileForm,SaltGroupForm
from sysadmin.models import SaltGroup,SaltHost

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from utils.config_parser import ConfParserClass
import json
from channels.layers import get_channel_layer
import os
import paramiko
from asgiref.sync import async_to_sync
from django.db.models import F
import datetime
from asset.models import ServerAsset
from sysadmin.models import DnsRecords

@login_required
def file_upload(request):
    '''
    文件上传界面
    '''
    if request.user.has_perm('deploy.view_filemanage'):
        tgt_list = ServerAsset.objects.all()
        data = {
            'tgt_list': tgt_list,
            'page_name': '文件上传'
        }
        return render(request, 'sysadmin/file_upload.html', data)
    else:
        raise Http404


@login_required
def remote_execution(request):
    '''
    salt远程命令界面
    '''
    if request.user.has_perm('deploy.view_deploy'):
        if request.method == 'GET':
            tgt_list = ServerAsset.objects.all()
            data = {
                'tgt_list': tgt_list,
                'page_name': '远程命令'
            }

            return render(request, 'sysadmin/remote_exec.html', data)

        else:
            print(request.POST)
            host = request.POST.getlist('host[]',[])
            # command = request.POST.get('command','')

            # 保险起见，命令先写死
            command = 'ls /root'
            if host and command:
                res = []
                for x in host:
                    cp = ConfParserClass('conf/settings.conf')
                    salt_url = cp.get('saltstack', 'url')
                    salt_username = cp.get('saltstack', 'username')
                    salt_password = cp.get('saltstack', 'password')

                    sapi = SaltApi(url=salt_url, username=salt_username, password=salt_password)
                    c = sapi.remote_execution(x, 'cmd.run',command)
                    res.append(c)

                    Message.objects.create(type=u'系统管理', user=request.user, action='远程命令',
                                           action_ip=UserIP(request),
                                           content= u'command:{0},host:{1}'.format(command,host))
            else:
                res = []

            return JsonResponse(res,safe=False)
    else:
        raise Http404


def aliyun_dns_list(request):
    cps = ConfParserClass('conf/settings.conf')
    client = AcsClient(cps.get('aliyun', 'accessKeyId'), cps.get('aliyun', 'accessSecret'), 'cn-hangzhou')

    req = CommonRequest()
    req.set_accept_format('json')
    req.set_domain('alidns.aliyuncs.com')
    req.set_method('POST')
    req.set_version('2015-01-09')
    req.set_action_name('DescribeDomainRecords')

    req.add_query_param('DomainName', 'dev4ops.cn')
    response = client.do_action_with_exception(req)
    response = str(response, encoding='utf-8')
    response = json.loads(response)['DomainRecords']['Record']

    for x in response:
        dr = {
            'rr': x['RR'],
            'status': x['Status'],
            'value': x['Value'],
            'type': x['Type'],
            'domainname': x['DomainName'],
            'ttl': x['TTL']
        }
        updated_values = {'rr': x['RR']}
        DnsRecords.objects.update_or_create(defaults=updated_values, **dr)

    if request.user.has_perm('asset.view_asset'):
        if request.method == 'GET':
            dr_list = DnsRecords.objects.all()

            data = {

                "page_name": '阿里云域名',
                "all_dns_list": dr_list
            }

            return render(request, 'sysadmin/dns_list.html', data)
    else:
        raise Http404


@login_required
def web_term(request):
    page_name = '发布详情'
    data = {
        "page_name": page_name,
    }
    return render(request, 'sysadmin/web_term.html', data)


def taillog(request, hostname, port, username, password, private, tail):
    """
    执行 tail log 接口
    """
    channel_layer = get_channel_layer()
    user = request.user.username
    os.environ[user] = "true"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        ssh.connect(hostname=hostname, port=port, username=username, password=password)
    else:
        pkey = paramiko.RSAKey.from_private_key_file("{0}".format(private))
        ssh.connect(hostname=hostname, port=port, username=username, pkey=pkey)
    cmd = "tail " + tail
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    for line in iter(stdout.readline, ""):
        print(1, os.environ.get(user))
        if os.environ.get(user) == 'false':
            break
        result = {"status": 0, 'data': line}
        result_all = json.dumps(result)
        async_to_sync(channel_layer.group_send)(user, {"type": "user.message", 'text': result_all})


@login_required
def web_log(request):
    if request.method == "GET":
        hosts = ServerAsset.objects.all()
        data = {
            "page_name": 'web日志',
            "hosts": hosts
        }
        return render(request, 'sysadmin/web_log.html', data)
    if request.method == "POST":
        status = request.POST.get('status', None)
        if not status:
            ret = {'status': True, 'error': None, }

            filepath = request.POST.get('filepath', None)
            host_id = request.POST.get('host', '')
            host_obj = ServerAsset.objects.get(id=host_id)
            ip = host_obj.public_ip
            port = 22
            username = host_obj.user.username
            password = host_obj.user.password
            private_key = host_obj.user.private_key

            if not filepath:
                ret['status'] = False
                ret['error'] = "请选择服务器,输入参数及日志地址."
                return HttpResponse(json.dumps(ret))

            try:
                taillog(request, ip, port, username, password, private_key, filepath)
            except Exception as e:
                ret['status'] = False
                ret['error'] = "错误{0}".format(e)
            return JsonResponse(ret)
        else:
            ret = {'status': True, 'error': None, }
            user = request.user.username
            os.environ[user] = "false"
            print(2, os.environ[user])
            return HttpResponse(json.dumps(ret))



try:
    import json
except ImportError:
    import simplejson as json
import datetime
import shutil


cps = ConfParserClass('conf/settings.conf')
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
        data = {
            'all_minions': minions,
            'all_minions_pre': minions_pre,
            'page_name': 'salt主机列表'
        }
        return render(request, 'asset/salt_key_list.html', data)
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
        data = {
            'all_groups': groups,
            'page_name': 'salt主机分组列表'
        }
        return render(request, 'asset/salt_group_list.html', data)
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

        data = {
            'form': form,
            'action': action,
            'page_name': page_name,
            'aid': id,
        }
        return render(request, 'asset/salt_group_manage.html',data)
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
def salt_history_list(request):
    '''
    任务列表
    '''
    if request.user.has_perm('userperm.view_message'):
        cp = ConfParserClass('conf/settings.conf')
        args = cp.items('saltstack',dict_type=True)
        sapi = SaltApi(**args)
        res = sapi.salt_history_jobs()[1]['return'][0]
        his = []
        for k,v in res.items():
            x = {}
            x['jid'] = k
            x = dict(x,**v)
            his.append(x)

        page_name = 'salt历史任务'
        data = {
            'page_name':page_name,
            'his':his
        }
        return render(request, 'saltstack/salt_history_list.html',data)
    else:
        raise Http404


@login_required
def salt_task_list(request):
    '''
    任务列表
    '''
    if request.user.has_perm('userperm.view_message'):
        if request.method == 'GET':
            if 'tid' in request.GET:
                tid = request.get_full_path().split('=')[1]
                log_detail = Message.objects.filter(user=request.user.first_name).filter(id=tid).exclude(
                    type=u'用户登录').exclude(type=u'用户退出')
                data = {
                    'log_detail': log_detail,
                    'page_name': 'salt任务列表'
                }
                return render(request, 'saltstack/salt_task_detail.html', data)

        logs = Message.objects.filter(user=request.user.first_name).exclude(type=u'用户登录').exclude(type=u'用户退出')[:200]
        data = {
            'all_logs': logs,
            'page_name': 'salt任务列表'
        }
        return render(request, 'saltstack/salt_task_list.html', data)
    else:
        raise Http404


@login_required
def salt_task_check(request):
    '''
    任务查询
    '''
    data = {
        'page_name': 'salt任务查询'
    }
    return render(request, 'saltstack/salt_task_check.html', data)


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
    data = {
        'page_name':'获取运行中的任务'
    }

    return render(request, 'saltstack/salt_task_running_list.html', data)
