from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import write_metadata
__author__ = "Alan Viars"
app_name = 'hashcow'
admin.autodiscover()


api_v1 = [
    url(r'write-metadata', write_metadata, name='write-metadata'),
]

urlpatterns = [
    path('api/v1/', include(api_v1)),
]

