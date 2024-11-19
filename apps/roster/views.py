from django.shortcuts import render
from django.http import JsonResponse
import logging
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import get_user_model


logger = logging.getLogger('register_.%s' % __name__)


User = get_user_model()


@login_required
def authenticated_enduser_home(request):
    template = "register/authenticated-home.html"
    context = {}
    return render(request, template, context)

def home(request):
    if request.user.is_authenticated:
        # Create user profile if one does not exist,
        return authenticated_enduser_home(request)
    template = "register/index.html"
    context = {}
    return render(request, template, context)
