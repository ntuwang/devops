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
from utils.mydb import MysqlConn


@login_required
def db_list(request):
    """
    cloud列表、cloud详细
    """

    if request.method == 'GET':

        return render(request, 'dba/db_list.html')

    elif request.method == 'POST':
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


@login_required
def db_dict(request):
    """
    cloud列表、cloud详细
    """

    if request.method == 'GET':
        record_list = list(DBInfo.objects.all().values())
        data = {'record_list': record_list,
                }

        return render(request, 'dba/db_dict.html',data)

    elif request.method == 'POST':
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


@login_required()
def get_table_list(request):
    cps = Conf_Parser('conf/settings.conf')
    db_id = request.POST.get('db_id','')
    dbinfo = DBInfo.objects.get(pk=db_id)
    db_username = cps.get('dba', 'username')
    db_pass = cps.get('dba', 'password')
    table_list = []

    data = {
        'status': 0,
        'message': '',
        'table_list': table_list
    }

    try:
        # 获取表名称
        with MysqlConn(dbinfo.db_ip, dbinfo.db_port, 'ptolemy', db_username,db_pass) as cur:
            sql = """show tables;"""
            cur.execute(sql)
            table_list = [table[0] for table in cur.fetchall()]

        data = {
            'status': 0,
            'message': '',
            'table_list': table_list
        }

    except Exception as e:
        data['status'] = 1
        data['message'] = '获取表名称时发生错误.'

    return HttpResponse(json.dumps(data), content_type='application/json')

