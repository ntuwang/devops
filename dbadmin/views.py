from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, StreamingHttpResponse
from utils.config_parser import ConfParserClass
import json
from utils.mydb import MysqlConn
from .forms import *
import traceback
from collections import OrderedDict
from django.core.serializers.json import DjangoJSONEncoder


@login_required
def database_list(request):
    """
    cloud列表、cloud详细
    """

    if request.method == 'GET':
        data = {
            'page_name': '数据库列表'
        }

        return render(request, 'dba/database_list.html',data)

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
        data = {
            'record_list': record_list,
            'page_name': '数据字典'
            }

        return render(request, 'dba/db_metadata.html', data)

    elif request.method == 'POST':
        cps = ConfParserClass('conf/settings.conf')
        db_id = request.POST.get('db_id', '')
        dbinfo = DBInfo.objects.get(pk=db_id)
        db_username = cps.get('dbadmin', 'username')
        db_pass = cps.get('dbadmin', 'password')
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

            with MysqlConn(dbinfo.db_ip, dbinfo.db_port, "information_schema", db_username, db_pass,
                           cursorclass=1) as cur:
                # 获取创建表的语句
                create_sql = """show create table {0}.{1};""".format(db_name, table_name)
                cur.execute(create_sql)
                table_create = cur.fetchone()['Create Table']

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

                columns_sql = """select column_name, 
                                     column_default, 
                                     is_nullable, 
                                     column_type, 
                                     column_comment, 
                                     column_key, extra 
                                 from information_schema.columns 
                                 where table_schema='{0}' and table_name='{1}';""".format(db_name, table_name)
                cur.execute(columns_sql)
                table_columns = cur.fetchall()

                data['table_create'] = table_create
                data['table_status'] = json.dumps(table_status, cls=DjangoJSONEncoder)
                data['table_index'] = table_index
                data['table_columns'] = table_columns
        except Exception as e:
            traceback.print_exc()
            data['status'] = 1
            data['message'] = '获取表元数据时发生错误.'

        context = {
            'data': data,
            'db_id': db_id,
            'table_name': table_name,
            'page_name': '数据字典明细'
        }
        return render(request, 'dba/db_metadata.html', context)


@login_required
def db_manage(request, aid=None, action=None):
    """
    Manage Cloud
    """
    page_name = ''
    if aid:
        db_list = get_object_or_404(DBInfo, pk=aid)
        if action == 'edit':
            page_name = '编辑数据库'
        if action == 'delete':
            db_list.delete()
            return redirect('database_list')
    else:
        db_list = DBInfo()
        action = 'add'
        page_name = '新增数据库'

    if request.method == 'GET':
        form = DBInfoForm(instance=db_list)
        data = {
            "form": form,
            "page_name": page_name,
            "action": action
        }
        return render(request, 'dba/db_manage.html', data)

    elif request.method == 'POST':
        form = DBInfoForm(request.POST, instance=db_list)

        if form.is_valid():
            if action == 'add':
                form.save()

            elif action == 'edit':
                form.save()
        return redirect('database_list')


@login_required()
def get_table_list(request):
    cps = ConfParserClass('conf/settings.conf')
    db_id = request.POST.get('db_id', '')
    dbinfo = DBInfo.objects.get(pk=db_id)
    db_username = cps.get('dbadmin', 'username')
    db_pass = cps.get('dbadmin', 'password')
    da_name = dbinfo.db_name
    table_list = []

    data = {
        'status': 0,
        'message': '',
        'table_list': table_list
    }

    try:
        # 获取表名称
        with MysqlConn(dbinfo.db_ip, dbinfo.db_port, da_name, db_username, db_pass) as cur:
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
