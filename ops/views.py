from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse

from django.forms.models import model_to_dict
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
from ops.models import DnsRecords

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
        return render(request, 'ops/file_upload.html', data)
    else:
        raise Http404


@login_required
def remote_execution(request):
    '''
    salt远程命令界面
    '''
    if request.user.has_perm('deploy.view_deploy'):
        tgt_list = ServerAsset.objects.all()
        data = {
            'tgt_list': tgt_list,
            'page_name': '远程命令'
        }

        return render(request, 'ops/remote_exec.html', data)
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

            return render(request, 'ops/dns_list.html', data)
    else:
        raise Http404


@login_required
def web_term(request):
    page_name = '发布详情'
    data = {
        "page_name": page_name,
    }
    return render(request, 'ops/web_term.html', data)


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
        return render(request, 'ops/web_log.html', data)
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
