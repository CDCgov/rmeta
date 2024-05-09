from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from .views import (annon_data_needs_csv, annon_data_needs_home,
                    state_report,state_report_index,
                    state_report_csv, type_csv, 
                    type_json,  jurisdiction_report,
                    jurisdiction_report_index, source_software_report_index, source_software_report,
                    program_area_report_index, program_area_report)

from .publicapi_views import public_type_csv, public_type_json, hello

__author__ = "Alan Viars"
app_name = 'report_meta'
admin.autodiscover()

app_v1 = [
    url(r'annon-data-needs/csv$', annon_data_needs_csv, name='annon_data_needs_csv'),
    url(r'annon-data-needs/home$', annon_data_needs_home, name='annon_data_needs_home'),
    url(r'reports/state/index$', state_report_index, name='state_report_index'),
    url(r'reports/jurisdiction/index$', jurisdiction_report_index, name='jurisdiction_report_index'),
    url(r'reports/source-software/index$', source_software_report_index, name='source_software_report_index'),
    url(r'reports/program-area/index$', program_area_report_index, name='program_area_report_index'),
    url(r'reports/state/csv$', state_report_csv, name='state_report_csv'),
    url(r'reports/state/(?P<state>[^/]+)$', state_report, name='state_report'),
    url(r'reports/jurisdiction/(?P<jurisdiction>[^/]+)$', jurisdiction_report, name='jurisdiction_report'),
    url(r'reports/source-software/(?P<software_code>[^/]+)$', source_software_report, name='source_software_report'),
    url(r'reports/program-area/(?P<program_area_code>[^/]+)$', program_area_report, name='program_area_report'),
    url(r'reports/state/(?P<state>[^/]+)$', state_report, name='state_report'),
    url(r'types/csv/(?P<my_type_name>[^/]+)$', login_required(type_csv), name='type_csv'),
    url(r'types/json/(?P<my_type_name>[^/]+)$', login_required(type_json), name='type_json'),
]

public_api_v1 = [

    url(r'public/hello$', hello, name='public_api_hello'),
    
    url(r'public/types/json/(?P<my_type_name>[^/]+)$', public_type_json, name='public_type_json'),
    url(r'public/types/csv/(?P<my_type_name>[^/]+)$', public_type_csv, name='public_type_csv'),


    url(r'public/types/csv/(?P<my_type_name>[^/]+)/(?P<my_module_name>[^/]+)$', public_type_csv, name='public_type_csv_module'),
    url(r'public/types/json/(?P<my_type_name>[^/]+)/(?P<my_module_name>[^/]+)$', public_type_json, name='public_type_json_module'),
]



urlpatterns = [
    path('app/v1/', include(app_v1)),
    path('v1/', include(public_api_v1)),
]

