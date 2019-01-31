from django.conf.urls import url

from dbadmin import views as dviews

# app_name = 'dbadmin'

urlpatterns = [

    url(r'^database_list/$', dviews.database_list, name='database_list'),
    url(r'^db_metadata/$', dviews.db_metadata, name='db_metadata'),
    url(r'^get_table_list/$', dviews.get_table_list, name='get_table_list'),

    url(r'^db_add/$', dviews.db_manage, name='db_add'),
    url(r'^db_edit/(?P<action>[\w-]+)/(?P<aid>\d+)/$', dviews.db_manage, name='db_manage'),

]
