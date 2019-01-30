"""devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls,name='admin'),
    path(r'', include('user.urls')),
    path(r'asset/', include('asset.urls')),
    path(r'salt/', include('saltstack.urls')),
    path(r'message/', include('message.urls')),
    path(r'ops/', include('ops.urls')),
    path(r'deploy/', include('deploy.urls')),
    path(r'dba/', include('dba.urls')),
]
