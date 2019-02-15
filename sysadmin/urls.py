from django.conf.urls import url

from sysadmin import views as oviews

# app_name = 'asset'

urlpatterns = [

    url(r'^file_manage/upload/$', oviews.file_upload, name='file_manage'),
    url(r'^remote_execution/$', oviews.remote_execution, name='remote_execution'),
    url(r'^dns/list/$', oviews.aliyun_dns_list, name='aliyun_dns_list'),

    url(r'^web_term/$', oviews.web_term, name='web_term'),
    url(r'^web_log/$', oviews.web_log, name='web_log'),

    url(r'^salt_key_list/$', oviews.salt_key_list, name='salt_key_list'),
    url(r'^salt_key_import/$', oviews.salt_key_import, name='salt_key_import'),
    url(r'^salt_key_manage/$', oviews.salt_key_manage, name='salt_key_manage'),
    url(r'^salt_group_list/$', oviews.salt_group_list, name='salt_group_list'),
    url(r'^salt_group_manage/add/$', oviews.salt_group_manage, name='salt_group_add'),
    url(r'^salt_group_manage/delete$', oviews.salt_group_manage, name='salt_group_delete'),
    url(r'^salt_group_manage/(?P<id>\d+)/edit/$', oviews.salt_group_manage, name='salt_group_edit'),

    url(r'^task_list/$', oviews.salt_task_list, name='task_list'),
    url(r'^salt_history_list/$', oviews.salt_history_list, name='salt_history_list'),
    url(r'^task_check/$', oviews.salt_task_check, name='task_check'),
    url(r'^task_running/$', oviews.salt_task_running, name='task_running'),
]
