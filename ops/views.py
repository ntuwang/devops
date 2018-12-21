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

        all_code_deploy = Deploys.objects.all().order_by('-created_at')[:10]

        return render(request, 'ops/code_deploy_list.html', {'all_code_deploy_list': all_code_deploy})
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
            deploy_list = get_object_or_404(Deploys, pk=aid)
            if action == 'edit':
                page_name = '编辑发布项目'
            elif action == 'delete':
                deploy_list.delete()
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
                # rundeploys.rollback(deploy)
                return redirect('code_deploy_progress', pk=deploy.id)


        else:
            deploy_list = Deploys()
            action = 'add'
            page_name = '新增发布项目'

        if request.method == 'POST':
            if action == 'add':
                data = request.POST.dict()
                data_new = {}
                project = Projects.objects.get(pk=data['project'])
                data_new['project'] = project
                data_new['user'] = request.user
                data_new['status'] = 3
                data_new['host'] = ServerAsset.objects.get(pk=data['name_host'])
                data_new['packs'] = ','.join(request.POST.getlist('name_pack'))
                # data_new['pack_url'] = '{0}/{1}/{2}/'.format(settings.FILESERVER,data['name_sprint'],data['name_build'])
                data_new['pack_url'] = ''
                data_new['jenkinsbd'] = data['name_jenkinsbd']
                data_new['branch'] = data['name_branch']
                print(data_new['packs'])
                data = data_new
                deploy = Deploys(**data)
                deploy.save()
                # rundeploys.deploy(deploy)
                return redirect('code_deploy_progress', pk=deploy.id)
        else:

            return render(request, 'code_deploy_manage.html', locals())
    else:
        raise Http404


@login_required
def code_deploy_progress(request, pk):
    deploy_id = pk
    page_name = '发布详情'
    return render(request, 'code_deploy_progress.html', locals())


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
