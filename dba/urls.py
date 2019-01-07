from django.conf.urls import url

from dba import views as dviews

# app_name = 'dba'

urlpatterns = [

    url(r'^db_list/$', dviews.db_list, name='db_list'),
    url(r'^db_dict/$', dviews.db_dict, name='db_dict'),
    url(r'^get_table_list/$', dviews.get_table_list, name='get_table_list'),

]
