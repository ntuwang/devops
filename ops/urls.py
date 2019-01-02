from django.conf.urls import url

from ops import views as oviews

# app_name = 'asset'

urlpatterns = [

    url(r'^file_manage/upload/$', oviews.file_upload, name='file_manage'),
    url(r'^remote_execution/$', oviews.remote_execution, name='remote_execution'),
    url(r'^project_list/$', oviews.project_list, name='project_list'),
    url(r'^project/add/$', oviews.project_manage, name='project_add'),
    url(r'^project/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', oviews.project_manage, name='project_manage'),
    url(r'^code_list/$', oviews.code_deploy_list, name='code_deploy_list'),
    url(r'^code/add/$', oviews.code_deploy_manage, name='code_deploy_add'),
    url(r'^(?P<pk>[0-9]+)/progress/$', oviews.code_deploy_progress, name='code_deploy_progress'),
    url(r'^code/view/(?P<aid>\d+)/(?P<action>[\w-]+)/$', oviews.code_deploy_manage, name='code_deploy_manage'),

    url(r'^dns/list/$', oviews.aliyun_dns_list, name='aliyun_dns_list'),

    url(r'^web_term/$', oviews.web_term, name='web_term'),
    url(r'^web_log/$', oviews.web_log, name='web_log'),

]
