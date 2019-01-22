from django.shortcuts import render
from message.models import Message
from django.http import Http404
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def log_audit(request):
    '''
    审计日志
    '''
    if request.user.is_superuser:
        logs = Message.objects.all()[:300]

        if request.method == 'GET':
            if 'aid' in request.GET:
                aid = request.get_full_path().split('=')[1]
                log_detail = Message.objects.filter(id=aid)
                data = {
                    'log_detail': log_detail,
                    'page_name': '日志明细'
                }
                return render(request, 'message/log_audit_detail.html',data)
        data = {
            'all_logs':logs,
            'page_name':'审计日志'
        }

        return render(request, 'message/log_audit.html', data)
    else:
        raise Http404
