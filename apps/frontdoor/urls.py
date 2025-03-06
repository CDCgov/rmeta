from django.conf.urls import include
from django.urls import re_path as url
from django.urls import path
from django.contrib import admin
from .views import (home, submission_form)
from .api_views import (api_home, restful_singleton_submission, view_submission)
__author__ = "Alan Viars"
app_name = 'frontfoor'
admin.autodiscover()


api_v1 = [
    url(r'$', api_home, name='api_home'),
    url(r'submit/singleton', restful_singleton_submission, name='restful_singleton_submission'),
    url(r'view/submission/(?P<transaction_control_number>[^/]+)', view_submission, name='view_submission'),
]


ui_v1 = [
    url(r'$', home, name='home'),
    url(r'submission-form/', submission_form, name='submission_form'),
]


urlpatterns = [
    path('', include(ui_v1)),
    path('api/', include(api_v1)),
]

