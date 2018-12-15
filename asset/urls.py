from django.conf.urls import url

from asset import views as aviews

# app_name = 'asset'

urlpatterns = [

    url(r'^salt_key_list/$', aviews.salt_key_list, name='salt_key_list'),
    url(r'^salt_key_import/$', aviews.salt_key_import, name='salt_key_import'),
    url(r'^salt_key_manage/$', aviews.salt_key_manage, name='salt_key_manage'),
    url(r'^salt_group_list/$', aviews.salt_group_list, name='salt_group_list'),
    url(r'^salt_group_manage/add/$', aviews.salt_group_manage, name='salt_group_add'),
    url(r'^salt_group_manage/delete$', aviews.salt_group_manage, name='salt_group_delete'),
    url(r'^salt_group_manage/(?P<id>\d+)/edit/$', aviews.salt_group_manage, name='salt_group_edit'),

    url(r'^asset/server_info/$', aviews.get_server_asset_info, name='server_info'),
    url(r'^server/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', aviews.server_asset_manage, name='server_manage'),
    url(r'^owner_list/$', aviews.owner_list, name='owner_list'),
    url(r'^owner/add/$', aviews.owner_manage, name='owner_add'),
    url(r'^owner/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', aviews.owner_manage, name='owner_manage'),
    url(r'^cloud_list/$', aviews.cloud_asset_list, name='cloud_asset_list'),
    url(r'^cloud/add/$', aviews.cloud_asset_manage, name='cloud_add'),
    url(r'^server/add/$', aviews.server_asset_manage, name='server_add'),
    url(r'^cloud/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', aviews.cloud_asset_manage, name='cloud_manage'),

]
