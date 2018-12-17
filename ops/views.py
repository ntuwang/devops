from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse
from user.models import Users
from asset.models import ServerAsset


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

