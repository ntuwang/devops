from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse
from user.models import Users
from asset.models import ServerAsset
from ops.models import Projects
from .forms import *
from django.forms.models import model_to_dict
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from utils.config_parser import Conf_Parser
import json
from channels.layers import get_channel_layer
import os
import paramiko
from asgiref.sync import async_to_sync
from .deploy import DeploysService, deploy_thread
from django.db.models import F
import datetime


# Create your views here.
@login_required
def file_upload(request):
    '''
    文件上传界面
    '''
    if request.user.has_perm('deploy.view_filemanage'):
        tgt_list = ServerAsset.objects.all()
        return render(request, 'ops/file_upload.html', {'tgt_list': tgt_list})
    else:
        raise Http404


@login_required
def remote_execution(request):
    '''
    salt远程命令界面
    '''
    if request.user.has_perm('deploy.view_deploy'):
        tgt_list = ServerAsset.objects.all()
        return render(request, 'ops/remote_exec.html', {'tgt_list': tgt_list})
    else:
        raise Http404


@login_required
def project_list(request):
    """
    cloud列表、cloud详细
    """
    if request.user.has_perm('asset.view_asset'):
        if request.method == 'GET':
            all_project = Projects.objects.all()

            return render(request, 'ops/project_list.html', {'all_project_list': all_project})
    else:
        raise Http404


@login_required
def project_manage(request, aid=None, action=None):
    """
    Manage Cloud
    """
    if request.user.has_perms(['asset.view_asset', 'asset.edit_asset']):
        page_name = ''
        if aid:
            project_list = get_object_or_404(Projects, pk=aid)
            if action == 'edit':
                page_name = '编辑发布项目'
            if action == 'delete':
                project_list.delete()
                return redirect('project_list')
        else:
            project_list = Projects()
            action = 'add'
            page_name = '新增发布项目'

        if request.method == 'POST':
            form = ProjectsForm(request.POST, instance=project_list)

            if form.is_valid():
                if action == 'add':
                    form.save()
                    return redirect('project_list')
                if action == 'edit':
                    form.save()
                    return redirect('project_list')
        else:
            form = ProjectsForm(instance=project_list)

        return render(request, 'ops/project_manage.html', {"form": form, "page_name": page_name, "action": action})
    else:
        raise Http404


@login_required
def code_deploy_list(request):
    """
    cloud列表、cloud详细
    """
    if request.user.has_perm('asset.view_asset'):
        if request.method == 'GET':
            if 'aid' in request.GET:
                aid = request.get_full_path().split('=')[1]
                code_deploy_detail = Deploys.objects.filter(id=aid)
                return render(request, 'ops/code_deploy_list.html', {'code_deploy_detail': code_deploy_detail})
            return render(request, 'ops/code_deploy_list.html')

        elif request.method == 'POST':

            offset = int(request.POST.get('offset'))
            limit = int(request.POST.get('limit'))
            limit = offset + limit

            record_list = Deploys.objects.all().values(
                'id',
                'branch',
                'status',
                'created_at',
                user_username=F('user__username'),
                project_name=F('project__name'),
            )

            search = request.POST.get('search', '')
            try:
                search_1 = int(search)
            except:
                search_1 = ''
            if search:
                if search_1:
                    record_list = [i for i in record_list if search in i.values() or search_1 in i.values()]

                else:
                    record_list = [i for i in record_list if search in i.values()]

            data = {'total': len(record_list),
                    'rows': record_list[offset:limit],
                    }
            return JsonResponse(data)

    else:
        raise Http404


@login_required
def code_deploy_manage(request, aid=None, action=None):
    """
    Manage Cloud
    """
    if request.user.has_perms(['asset.view_asset', 'asset.edit_asset']):
        page_name = ''
        if aid:
            deploy_obj = get_object_or_404(Deploys, pk=aid)
            if action == 'edit':
                page_name = '编辑发布项目'
            elif action == 'delete':
                deploy_obj.delete()
                return redirect('code_deploy_list')
            elif action == 'get':
                """获取进度信息"""
                deploy_detail = model_to_dict(Deploys.objects.get(id=aid))
                return JsonResponse(dict(rc=0, data=deploy_detail))
            elif action == 'rollback':
                deploy = Deploys.objects.get(pk=aid)
                deploy.progress = 0
                deploy.status = 3
                deploy.save()

                return redirect('code_deploy_progress', pk=deploy.id)
            elif action == 'progress':
                deploy_id = aid
                page_name = '发布详情'
                return render(request, 'ops/code_deploy_progress.html', locals())

        else:
            deploy_obj = Deploys()
            action = 'add'
            page_name = '新增发布项目'

        if request.method == 'POST':
            form = DeploysForm(request.POST, instance=deploy_obj)

            if form.is_valid():
                if action == 'add':
                    deploy = form.save(commit=False)
                    deploy.user = Users.objects.get(username=request.user)
                    deploy.status = 3
                    deploy.save()
                    d = DeploysService(deploy.id)
                    d.start_deploy()

                    return redirect('code_deploy_manage', action='progress', aid=deploy.id)
                if action == 'edit':
                    form.save()
                    return redirect('code_deploy_list')
        else:
            form = DeploysForm(instance=deploy_obj)

        return render(request, 'ops/code_deploy_manage.html', {"form": form, "page_name": page_name, "action": action})

    else:
        raise Http404


def aliyun_dns_list(request):
    cps = Conf_Parser('conf/settings.conf')
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

            return render(request, 'ops/dns_list.html', {'all_dns_list': dr_list})
    else:
        raise Http404


@login_required
def web_term(request):
    page_name = '发布详情'
    return render(request, 'ops/web_term.html', locals())


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
        return render(request, 'ops/web_log.html', {"hosts": hosts})
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
