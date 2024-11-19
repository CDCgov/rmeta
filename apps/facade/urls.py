from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import (home)
author__ = "Alan Viars"
app_name = 'facade'
admin.autodiscover()

app_v1 = [
    url(r'$', home, name='home'),
]



urlpatterns = [
    path('', include(app_v1)),
]

