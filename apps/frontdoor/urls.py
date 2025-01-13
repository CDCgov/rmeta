from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import (home, fhirspec_process_message, generic_process_message)
app_name = 'frontfoor'
admin.autodiscover()


api_v1 = [
    url(r'apis/fhir/$process-message$', fhirspec_process_message, name='fhirspec_process_message'),
    url(r'apis/upload/(?P<origin_id>[^/]+)/(?P<message_type>[^/]+)/message$', generic_process_message, name='generic_process_message'),
]


ui_v1 = [
    url(r'$', home, name='home'),
    url(r'upload-form/', home, name='upload-form'),
]


urlpatterns = [
    path('', include(ui_v1)),
    path('api/', include(api_v1)),
]

