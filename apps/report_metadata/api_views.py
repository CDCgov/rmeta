from django.shortcuts import render
from django.http import JsonResponse
import logging
from oauth2_provider.decorators import protected_resource
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from oauth2_provider import views as oauth2_views
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import RMetaMessage
from django.http import HttpResponse
from datetime import datetime
import csv
import importlib

logger = logging.getLogger('report_metadata_message_api.%s' % __name__)
User = get_user_model()


@require_GET
@protected_resource()
def hello_oauth(request):
    # A remote API call for logging out the user
    user = request.resource_owner
    message = "Hello OAuth World, %s" % (user.first_name)
    data = {"status": "ok",
            "message": message}
    logger.info(message)
    return JsonResponse(data)



@require_GET
def hello(request):
    # A remote API call for logging out the user
    message = "Hello World"
    data = {"status": "ok",
            "message": message}
    logger.info(message)
    return JsonResponse(data)
