from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import (hello, source_list, recipient_system_list, 
                    annon_data_needs_csv, annon_data_needs_home,
                    state_report,state_report_index,
                    state_report_csv,jurisdictions_csv, type_csv, 
                    type_json,  jurisdiction_report,
                    jurisdiction_report_index, source_software_report_index, source_software_report,
                    program_area_report_index, program_area_report)
__author__ = "Alan Viars"
app_name = 'rdata'
admin.autodiscover()

app_v1 = [
    url(r'source/system/list$', source_list, name='source_list'),
    url(r'recipient/system/list$', recipient_system_list, name='recipient_system_list'),
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
    url(r'reports/state/(?P<state>[^/]+)$', state_report, name='state_report'),
    url(r'types/jurisdictions$', jurisdictions_csv, name='jurisdictions_csv'),
    url(r'types/csv/(?P<my_type_name>[^/]+)$', type_csv, name='type_csv'),
    url(r'types/json/(?P<my_type_name>[^/]+)$', type_json, name='type_json'),
]

api_v1 = [
    url(r'hello$', hello, name='hello'),
]

urlpatterns = [
    path('app/v1/', include(app_v1)),
    path('api/v1/', include(api_v1)),
]

