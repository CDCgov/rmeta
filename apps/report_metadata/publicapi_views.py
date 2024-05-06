from django.shortcuts import render
from django.http import JsonResponse
import logging
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from oauth2_provider import views as oauth2_views
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseForbidden
from datetime import datetime
import csv
import importlib
from django_ratelimit.decorators import ratelimit

logger = logging.getLogger('report_metadata_message_api.%s' % __name__)
User = get_user_model()

ALLOWED_TYPES =('Jurisdiction', 'SourceSoftware', 'ProgramAreaType', 
                'DomainType', 'DataClassType', 'DataElementType', 'UseCaseType')


@require_GET
def hello(request):
    # A remote API call for logging out the user
    message = "Hello World"
    data = {"status": "ok",
            "message": message}
    logger.info(message)
    return JsonResponse(data)


@require_GET
@ratelimit(key='ip', rate='100/h')
def public_type_csv(request, my_type_name, my_module_name="report_metadata"):
    module_name = "apps." + my_module_name + ".models" 
    if my_type_name not in ALLOWED_TYPES:
        return HttpResponseForbidden()
    MyClass = getattr(importlib.import_module(module_name), my_type_name)
    js = MyClass.objects.all()
    filename = my_type_name +"-types-" + datetime.now().strftime('%m-%d-%Y') + ".csv"
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=' + filename
    writer = csv.DictWriter(response, js[0].as_dict.keys())
    writer.writeheader()
    for i in js:
        writer.writerow(i.as_dict)
    return response

@require_GET
@ratelimit(key='ip', rate='100/h')
def public_type_json(request, my_type_name, my_module_name="report_metadata"):
    module_name = "apps." + my_module_name + ".models" 
    if my_type_name not in ALLOWED_TYPES:
        return HttpResponseForbidden()
    MyClass = getattr(importlib.import_module(module_name), my_type_name)
    js = MyClass.objects.all()
    filename = datetime.now().strftime('%m-%d-%Y') + "-" + my_type_name +"-types.json"
    count=0
    json_results = {"count": count,
                    #"updated": datetime.now().strftime('%m-%d-%Y'),
                    "content":[]}
    for i in js:
        json_results["content"].append(i.as_dict)
        json_results["count"] += 1
    response = JsonResponse(json_results)
    return response