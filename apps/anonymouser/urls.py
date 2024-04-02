from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import anonymize
__author__ = "Alan Viars"
app_name = 'anonymouser'
admin.autodiscover()


api_v1 = [
    url(r'anonymize', anonymize, name='anonymize'),
]

urlpatterns = [
    path('api/v1/', include(api_v1)),
]
