from django.conf.urls import url

from ops import views as oviews

# app_name = 'asset'

urlpatterns = [

    url(r'^file_manage/upload/$', oviews.file_upload, name='file_manage'),
    url(r'^remote_execution/$', oviews.remote_execution, name='remote_execution'),
    url(r'^project_list/$', oviews.project_list, name='project_list'),
    url(r'^project/add/$', oviews.project_manage, name='project_add'),
    url(r'^project/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', oviews.project_manage, name='project_manage'),

]
