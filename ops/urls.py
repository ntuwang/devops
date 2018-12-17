from django.conf.urls import url

from ops import views as oviews

# app_name = 'asset'

urlpatterns = [

    url(r'^file_manage/upload/$', oviews.file_upload, name='file_manage'),
    url(r'^remote_execution/$', oviews.remote_execution, name='remote_execution'),

]
