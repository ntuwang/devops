from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse
from user.models import Users
from asset.models import ServerAsset
from ops.models import Projects
from dba.models import DBInfo
from utils.config_parser import Conf_Parser
import json


@login_required
def db_list(request):
    """
    cloud列表、cloud详细
    """

    if request.method == 'GET':

        return render(request, 'dba/db_list.html')

    elif request.method == 'POST':
        print(request.POST)
        offset = int(request.POST.get('offset'))
        limit = int(request.POST.get('limit'))
        limit = offset + limit
        record_list = list(DBInfo.objects.all().values())

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
        return JsonResponse(data, safe=False)
