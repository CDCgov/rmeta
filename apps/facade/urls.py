from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import (home, fhirspec_process_message, generic_process_message)
author__ = "Alan Viars"
app_name = 'facade'
admin.autodiscover()

app_v1 = [
    url(r'$', home, name='home'),
    url(r'apis/fhir/$process-message$', fhirspec_process_message, name='fhirspec_process_message'),
    url(r'apis/upload/(?P<origin_id>[^/]+)/(?P<message_type>[^/]+)/message$', generic_process_message, name='generic_process_message'),
]



urlpatterns = [
    path('', include(app_v1)),
]

