from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import TransactionForm
from django.http import JsonResponse
import logging
from oauth2_provider.decorators import protected_resource
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_GET
from django.contrib.auth import get_user_model
from oauth2_provider import views as oauth2_views
from django.conf import settings
from django.urls import reverse

def home(request):
    return render(request, 'facade/home.html')


def fhir_process_message(request, message_type):
    return JsonResponse({'status': 'ok'})

def fhirspec_process_message(request, message_type):
    return JsonResponse({'status': 'ok'})


def hl7v2_process_message(request, message_type):
    if message_type == 'hl7v2':
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})

def csv_process_message(request, message_type):
    if message_type == 'csv':
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})

def generic_process_message(request,message_type):
    if message_type == 'hl7v2':
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})

def generic_process_message(request, message_type, origin_id):
    if message_type == 'hl7v2':
        return hl7v2_process_message(request, "hl7v2", origin_id)
    elif message_type == 'fhir':
        return fhir_process_message(request, "fhir", origin_id)
    elif message_type == 'csv':
        return csv_process_message(request, "csv", origin_id)
    
    JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})


@login_required
def submit(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TransactionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('submission_url', args=('',)))

    return render(request, 'frontdoor/submit.html')