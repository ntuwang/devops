from django.conf.urls import url

from deploy import views as dviews

# app_name = 'asset'

urlpatterns = [

    url(r'^project_list/$', dviews.project_list, name='project_list'),
    url(r'^project/add/$', dviews.project_manage, name='project_add'),
    url(r'^project/edit/(?P<action>[\w-]+)/(?P<aid>\d+)/$', dviews.project_manage, name='project_manage'),
    url(r'^deploy_list/$', dviews.code_deploy_list, name='code_deploy_list'),
    url(r'^deploy_add/$', dviews.code_deploy_manage, name='code_deploy_add'),
    url(r'^deploy_manage/(?P<action>[\w-]+)/(?P<aid>\d+)/$', dviews.code_deploy_manage, name='code_deploy_manage'),
    url(r'^jenkins_list/$', dviews.jenkins_list, name='jenkins_list'),

]
