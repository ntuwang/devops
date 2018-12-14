from django.conf.urls import url
from django.contrib.auth import views as djviews
from . import views

# app_name = 'user'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/$', views.login, name='login'),
    url(r'^accounts/logout/$', views.logout, {'next_page': '/'}, name='logout'),
]
