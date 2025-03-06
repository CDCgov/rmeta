from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import SubmissionForm
from .models import Origin
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
    return render(request, 'frondoor/home.html')


def fhirspec_process_message(request, ori):
    return JsonResponse({'status': 'ok'})


def generic_process_message(request, origin_code):
    # Check if ORI is valid
    origin = Origin.objects.get(code=origin_code)
    if not origin:
        return JsonResponse({'status': 'fail', 'message': 'Invalid origin'})
    # Write transaction/message to data store
    return JsonResponse({'status': 'ok-json', 'origin': origin.name})


@login_required
def submission_form(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubmissionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('submission_url', args=('',)))

    return render(request, 'frontdoor/submit.html')