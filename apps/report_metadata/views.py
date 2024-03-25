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
from .models import (AnonyomizedDataNeed, Connection, 
                     Jurisdiction, SourceSystem, SourceSoftware,
                     ProgramAreaType)
from django.http import HttpResponse
from datetime import datetime
import csv
import importlib
from django.contrib import messages


logger = logging.getLogger('report_metadata_.%s' % __name__)


User = get_user_model()

@login_required
def state_report_index(request):
    jurisdictions = Jurisdiction.objects.filter(state_level=True)
    template = "report_metadata/state-report-index.html"
    context = {"jurisdictions":jurisdictions}
    return render(request, template, context)


@login_required
def jurisdiction_report_index(request):
    jurisdictions = Jurisdiction.objects.all()
    template = "report_metadata/reports-by-jurisdiction.html"
    context = {"jurisdictions":jurisdictions}
    return render(request, template, context)

@login_required
def source_software_report_index(request):
    software = SourceSoftware.objects.all()
    template = "report_metadata/reports-by-data-source-software.html"
    context = {"software":software}
    return render(request, template, context)


@login_required
def program_area_report_index(request):
    program_areas = ProgramAreaType.objects.all()
    template = "report_metadata/reports-by-program-area.html"
    context = {"program_areas":program_areas}
    return render(request, template, context)


@login_required
def source_software_report(request, software_code):
    software = SourceSoftware.objects.get(code=software_code)
    connections =Connection.objects.filter(source_system__software__code=software_code)
    systems =SourceSystem.objects.filter(software__code=software_code)
    print(len(systems))
    template = "report_metadata/source-software-report.html"
    context = {"name": "Source Software", "software": software,
               "connections": connections, "systems":systems}
    return render(request, template, context)


@login_required
def program_area_report(request, program_area_code):
    program_area = ProgramAreaType.objects.get(code=program_area_code)
    connections =Connection.objects.filter(source_system__program_areas__code=program_area_code)
    systems =SourceSystem.objects.filter(program_areas__code=program_area_code)
    print(len(systems))
    template = "report_metadata/program-area-report.html"
    context = {"name": "Program Area", "program_area": program_area,
               "connections": connections, "systems":systems}
    return render(request, template, context)


@login_required
def state_report(request, state):
    connections = Connection.objects.filter(partner__state=state)
    systems = SourceSystem.objects.filter(jurisdiction__state=state)
    jurisdiction = Jurisdiction.objects.get(state=state, state_level=True)
    template = "report_metadata/state-report.html"
    context = {"connections":connections, "state":state, "systems": systems,
               "name": "Jurasdiction", "jurisdiction":jurisdiction}
    return render(request, template, context)

@login_required
def jurisdiction_report(request, jurisdiction):
    connections = Connection.objects.filter(partner__jurisdiction__code=jurisdiction)
    systems = SourceSystem.objects.filter(jurisdiction__code=jurisdiction)
    jurisdiction = Jurisdiction.objects.get(code=jurisdiction)
    template = "report_metadata/state-report.html"
    context = {"connections":connections, "state":jurisdiction, 
               "systems": systems,
               "name": "Jurasdiction", "jurisdiction":jurisdiction}
    return render(request, template, context)


@login_required
def state_report_csv(request):
    cs = Connection.objects.filter(partner__jurisdiction__state_level=True)
    filename = datetime.now().strftime('%m-%d-%Y') + "state-to-cdc-system-connectivity-report.csv"
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=' + filename
    writer = csv.DictWriter(response, cs[0].as_dict.keys())
    writer.writeheader()
    for i in cs:
        writer.writerow(i.as_dict)
    return response

@login_required
def jurisdictions_csv(request):
    js = Jurisdiction.objects.all()
    filename = datetime.now().strftime('%m-%d-%Y') + "jurisdictions.csv"
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=' + filename
    writer = csv.DictWriter(response, js[0].as_dict.keys())
    writer.writeheader()
    for i in js:
        writer.writerow(i.as_dict)
    return response

@login_required
def type_csv(request, my_type_name):
    MyClass = getattr(importlib.import_module("apps.report_metadata.models"), my_type_name)
    js = MyClass.objects.all()
    filename = my_type_name +"-types-" + datetime.now().strftime('%m-%d-%Y') + ".csv"
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=' + filename
    writer = csv.DictWriter(response, js[0].as_dict.keys())
    writer.writeheader()
    for i in js:
        writer.writerow(i.as_dict)
    return response

@login_required
def type_json(request, my_type_name):
    
    MyClass = getattr(importlib.import_module("apps.report_metadata.models"), my_type_name)
    js = MyClass.objects.all()
    filename = datetime.now().strftime('%m-%d-%Y') + "-" + my_type_name +"-types.json"
    
    #response['Content-Disposition'] = 'attachment; filename=' + filename
    count=0
    json_results = {"count": count,
                    "updated": datetime.now().strftime('%m-%d-%Y'),
                    "content":[]}
    for i in js:
        json_results["content"].append(i.as_dict)
        json_results["count"] += 1
    
    response = JsonResponse(json_results)
    return response



@login_required
def annon_data_needs_csv(request):
    adns = AnonyomizedDataNeed.objects.all()
    filename = datetime.now().strftime('%m-%d-%Y') + "anondata.csv"
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=' + filename
    writer = csv.DictWriter(response, adns[0].as_dict.keys())
    writer.writeheader()
    for i in adns:
        writer.writerow(i.as_dict)
    return response

@login_required
def annon_data_needs_home(request):
    return render(request, "report_metadata/annon-data-needs.html", {})

@login_required
def authenticated_enduser_home(request):
    template = "report_metadata/authenticated-home.html"
    context = {}
    return render(request, template, context)

def home(request):
    if request.user.is_authenticated:
        # Create user profile if one does not exist,
        return authenticated_enduser_home(request)
    template = "report_metadata/index.html"
    context = {}
    return render(request, template, context)


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

@require_GET
def source_list(request):
    # A remote API call for logging out the user
    message = "Source Systems"
    data = {"status": "ok",
            "message": message}
    logger.info(message)
    return JsonResponse(data)

@require_GET
def recipient_system_list(request):
    # A remote API call for logging out the user
    message = "Recipient Systems"
    data = {"status": "ok",
            "message": message}
    logger.info("Hello world.")
    return JsonResponse(data)