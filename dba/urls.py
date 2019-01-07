from django.conf.urls import url

from dba import views as dviews

# app_name = 'dba'

urlpatterns = [

    url(r'^db_list/$', dviews.db_list, name='db_list'),

]
