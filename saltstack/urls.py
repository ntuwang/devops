from django.conf.urls import url

from saltstack import views as sviews

# app_name = 'asset'

urlpatterns = [

    url(r'^salt_key_list/$', sviews.salt_key_list, name='salt_key_list'),
    url(r'^salt_key_import/$', sviews.salt_key_import, name='salt_key_import'),
    url(r'^salt_key_manage/$', sviews.salt_key_manage, name='salt_key_manage'),
    url(r'^salt_group_list/$', sviews.salt_group_list, name='salt_group_list'),
    url(r'^salt_group_manage/add/$', sviews.salt_group_manage, name='salt_group_add'),
    url(r'^salt_group_manage/delete$', sviews.salt_group_manage, name='salt_group_delete'),
    url(r'^salt_group_manage/(?P<id>\d+)/edit/$', sviews.salt_group_manage, name='salt_group_edit'),

]
