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
from .forms import *
import traceback


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
def db_metadata(request):
    """
    cloud列表、cloud详细
    """

    if request.method == 'GET':
        record_list = list(DBInfo.objects.all().values())
        data = {'record_list': record_list,
                }

        return render(request, 'dba/db_metadata.html', data)

    elif request.method == 'POST':
        cps = Conf_Parser('conf/settings.conf')
        db_id = request.POST.get('db_id', '')
        dbinfo = DBInfo.objects.get(pk=db_id)
        db_username = cps.get('dba', 'username')
        db_pass = cps.get('dba', 'password')
        db_name = dbinfo.db_name

        table_name = request.POST.get('table_name', '')

        table_create = ''
        table_status = {}
        table_index = {}

        data = {
            'status': 0,
            'message': '',
            'table_create': table_create,
            'table_status': table_status,
            'table_index': table_index
        }

        try:
            # 获取表元数据

            with MysqlConn(dbinfo.db_ip, dbinfo.db_port,"information_schema", db_username, db_pass,) as cur:
                # 获取创建表的语句
                create_sql = """show create table {0}.{1};""".format(db_name, table_name)
                cur.execute(create_sql)
                table_create = cur.fetchone()[1]

                # 获取表统计信息
                status_sql = """
                    SELECT table_schema,
                           table_name,
                           table_type,
                           engine,
                           version,
                           row_format,
                           table_rows,
                           avg_row_length,
                           data_length,
                           max_data_length,
                           index_length,
                           data_free,
                           auto_increment,
                           create_time,
                           update_time,
                           check_time,
                           table_collation,
                           checksum,
                           create_options,
                           table_comment
                    FROM tables
                    WHERE TABLE_schema = '{0}' AND TABLE_NAME = '{1}';
                """.format(db_name, table_name)
                cur.execute(status_sql)
                table_status = cur.fetchone()

                # 获取表索引信息
                index_sql = """
                    SELECT INDEX_NAME,
                           SEQ_IN_INDEX,
                           COLUMN_NAME,
                           COLLATION,
                           CARDINALITY,
                           CASE NON_UNIQUE WHEN 0 THEN 'YES' ELSE 'NO' END AS IS_UNIQUE,
                           NULLABLE,
                           INDEX_TYPE,
                           COLLATION,
                           INDEX_COMMENT
                    FROM STATISTICS
                    WHERE TABLE_schema = '{0}' AND TABLE_NAME = '{1}';
                """.format(db_name, table_name)
                cur.execute(index_sql)
                table_index = cur.fetchall()

                data['table_create'] = table_create
                data['table_status'] = table_status
                data['table_index'] = table_index
        except Exception as e:
            traceback.print_exc()
            data['status'] = 1
            data['message'] = '获取表元数据时发生错误.'

        context = {
            'data': data,
            'db_id': db_id,
            'table_name': table_name,
        }
        return render(request, 'dba/db_metadata.html', context)


@login_required
def db_manage(request, aid=None, action=None):
    """
    Manage Cloud
    """
    if request.user.has_perms(['asset.view_asset', 'asset.edit_asset']):
        dbinfo = DBInfo()

        if request.method == 'GET':
            form = DBInfoForm(instance=dbinfo)
            page_name = ''
            if aid:
                project_list = get_object_or_404(Projects, pk=aid)
                if action == 'edit':
                    page_name = '编辑发布项目'
                if action == 'delete':
                    project_list.delete()
                    return redirect('project_list')
            else:
                action = 'add'
                page_name = '新增发布项目'
            return render(request, 'ops/project_manage.html', {"form": form, "page_name": page_name, "action": action})

        elif request.method == 'POST':
            form = DBInfoForm(request.POST, instance=dbinfo)

            if form.is_valid():
                form.save()
            return redirect('db_list')
    else:
        raise Http404



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

