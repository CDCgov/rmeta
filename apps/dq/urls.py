from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import index
author__ = "Alan Viars"
app_name = 'dq'
admin.autodiscover()


urlpatterns = [
    url(r'$', index, name='index'),
]
