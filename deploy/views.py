from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse

from deploy.models import Projects
from .forms import ProjectsForm, DeploysForm
from django.forms.models import model_to_dict
from .scripts import DeploysService, deploy_thread
from django.db.models import F
from .models import Deploys, Projects
from user.models import Users
from utils.jenkins_job import JenkinsJob
from utils.config_parser import ConfParserClass
from user.models import Message

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
def project_list(request):
    """
    cloud列表、cloud详细
    """
    if request.user.has_perm('asset.view_asset'):
        if request.method == 'GET':
            all_project = Projects.objects.all()
            data = {
                'all_project_list': all_project,
                'page_name': '项目列表'
            }

            return render(request, 'deploy/project_list.html', data)
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
        data = {
            "form": form,
            "page_name": page_name,
            "action": action
        }

        return render(request, 'deploy/project_manage.html', data)
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
                data = {
                    'page_name': '发布明细',
                    'code_deploy_detail': code_deploy_detail
                }
                return render(request, 'deploy/code_deploy_list.html', data)
            data = {
                'page_name': '发布列表',
            }
            return render(request, 'deploy/code_deploy_list.html', data)

        elif request.method == 'POST':

            offset = int(request.POST.get('offset'))
            limit = int(request.POST.get('limit'))
            limit = offset + limit

            record_list = Deploys.objects.all().values(
                'id',
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
    Manage code deploy
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
                deploy.status = 1
                deploy.save()

                return redirect('code_deploy_progress', pk=deploy.id)
            elif action == 'progress':

                data = {
                    'deploy_id': aid,
                    'page_name': '发布过程',
                }
                return render(request, 'deploy/code_deploy_progress.html', data)

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

        data = {
            "form": form,
            "page_name": page_name,
            "action": action
        }
        return render(request, 'deploy/code_deploy_manage.html', data)

    else:
        raise Http404


@login_required
def jenkins_manage(request, j_name=None, action=None):
    """
    Manage Jenkins
    """
    if request.user.has_perms(['asset.view_asset', 'asset.edit_asset']):
        cp = ConfParserClass('conf/settings.conf')
        J = JenkinsJob(cp.get('jenkins', 'url'), cp.get('jenkins', 'username'), cp.get('jenkins', 'password'))
        if action == 'add':
            pass
        elif action == 'list':
            if request.method == 'GET':
                page_name = 'Jenkins 管理'

                return render(request, 'deploy/jenkins_list.html', {'page_name': page_name})
            elif request.method == 'POST':
                job_names = J.job_list()
                job_list = [J.job_query(j) for j in job_names]
                data = {
                    'total': len(job_list),
                    'rows': job_list
                }
                return JsonResponse(data)

        elif action == 'edit':  # 编辑构建项目
            page_name = '编辑构建项目'
        elif action == 'delete':  # 删除构建项目
            pass
        elif action == 'view':  # 查看构建项目
            """获取console信息"""
            ret = J.job_console(j_name)
            data = {
                'ret':ret,
                'j_name':j_name,
                'page_name':'日志详情'
            }
            return render(request,'deploy/jenkins_detail.html',data)
        elif action == 'build':  # 开始构建项目
            Message.objects.create(type=u'部署管理', user=request.user, action='构建jenkins',
                                   action_ip=UserIP(request),
                                   content=u'JOB名称:{0}'.format(j_name))
            try:
                ret = J.job_build(j_name)
            except:
                pass
        return redirect('jenkins_manage',action='list')

    else:
        raise Http404

