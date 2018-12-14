from django.conf.urls import url
from django.contrib.auth import views as djviews
from . import views as uviews

# app_name = 'user'

urlpatterns = [

    url(r'^log_audit/$', uviews.log_audit, name='log_audit'),

]
