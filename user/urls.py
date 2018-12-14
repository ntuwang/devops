from django.conf.urls import url
from django.contrib.auth import views as djviews
from . import views as uviews

# app_name = 'user'

urlpatterns = [
    url(r'^$', uviews.index, name='index'),
    url(r'^accounts/login/$', uviews.login, name='login'),
    url(r'^accounts/logout/$', uviews.logout, {'next_page': '/'}, name='logout'),
    url(r'^userauth/user/list/$', uviews.user_list, name='user_list'),
    url(r'^userauth/user/add/$', uviews.user_manage, name='user_add'),
    url(r'^userauth/user/edit/(?P<aid>\d+)/(?P<action>[\w-]+)/$', uviews.user_manage, name='user_manage'),
]
