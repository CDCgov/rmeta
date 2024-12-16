from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import check_data_element_common_name
author__ = "Alan Viars"
app_name = 'sophv'
admin.autodiscover()

app_v1 = [
    url(r'api/(?P<common_name>[^/]+)/(?P<message_type>[^/]+)/(?P<code>[^/]+)', 
        check_data_element_common_name, 
        name='check_data_element_common_name'),
    url(r'api/(?P<common_name>[^/]+)', 
        check_data_element_common_name, 
        name='data_element_common_name'),

]



urlpatterns = [
    path('', include(app_v1)),
]

