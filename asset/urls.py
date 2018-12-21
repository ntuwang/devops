from django.conf.urls import url
from django.urls  import path
from asset import views as aviews

# app_name = 'asset'

urlpatterns = [

    url(r'^server_info/$', aviews.get_server_asset_info, name='server_info'),
    url(r'^server/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', aviews.server_asset_manage, name='server_manage'),
    url(r'^owner_list/$', aviews.owner_list, name='owner_list'),
    url(r'^owner/add/$', aviews.owner_manage, name='owner_add'),
    url(r'^owner/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', aviews.owner_manage, name='owner_manage'),
    url(r'^cloud_list/$', aviews.cloud_asset_list, name='cloud_asset_list'),
    url(r'^cloud/add/$', aviews.cloud_asset_manage, name='cloud_add'),
    url(r'^server/add/$', aviews.server_asset_manage, name='server_add'),
    url(r'^cloud/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', aviews.cloud_asset_manage, name='cloud_manage'),

    path('asset-webssh.html', aviews.asset_web_ssh, name='asset_web_ssh'),

]
