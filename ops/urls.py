from django.conf.urls import url

from ops import views as oviews

# app_name = 'asset'

urlpatterns = [

    url(r'^file_manage/upload/$', oviews.file_upload, name='file_manage'),
    url(r'^remote_execution/$', oviews.remote_execution, name='remote_execution'),
    url(r'^dns/list/$', oviews.aliyun_dns_list, name='aliyun_dns_list'),

    url(r'^web_term/$', oviews.web_term, name='web_term'),
    url(r'^web_log/$', oviews.web_log, name='web_log'),

]
