#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4

from collections import OrderedDict
from functools import update_wrapper
from django.http import HttpResponse
import json

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def kickout_401(reason, status_code=401):
    response = OrderedDict()
    response["code"] = status_code
    response["status"] = "Authentication error"
    response["errors"] = [reason, ]
    return HttpResponse(json.dumps(response, indent=2),
                        content_type="application/json")


def kickout_400(reason, status_code=400):
    response = OrderedDict()
    response["code"] = status_code
    response["status"] = "Client error"
    response["errors"] = [reason, ]
    return HttpResponse(json.dumps(response, indent=2),
                        content_type="application/json")


def kickout_404(reason, status_code=404):
    response = OrderedDict()
    response["code"] = status_code
    response["status"] = "NOT FOUND"
    response["errors"] = [reason, ]
    return HttpResponse(json.dumps(response, indent=2),
                        content_type="application/json")


def kickout_500(reason, status_code=500):
    response = OrderedDict()
    response["code"] = status_code
    response["status"] = "SERVER SIDE ERROR"
    response["errors"] = [reason, ]
    return HttpResponse(json.dumps(response, indent=2),
                        content_type="application/json")
