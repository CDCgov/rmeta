from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import HashedMessage
import json
from .helpers import kickout_400
import sys
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def write_metadata(request):
    if request.method in ('POST', 'PUT'):

        # Check if request body is JSON ------------------------
        try:
            j = json.loads(request.body.decode())
            if not isinstance(j, type({})):
                kickout_400(
                    "The request body did not contain a JSON object i.e. {}.")
        except:
            print(str(sys.exc_info()))
            return kickout_400("The request body did not contain valid JSON.")
        response = {"status":"ok"}
        # Attempt Create or Update
        # 
        dbfields = [f.name for f in HashedMessage._meta.get_fields()]
        dbfields.remove("id")
        dbfields.remove("hashlink")
        #del j['id']
        #del j['hashlink']
        update_dict = {}
        update_keys = []
        for k,v in j.items():
            if v:
                update_dict[k]=j[k]
                update_keys.append(k)
        save_to_hm = None

        print(update_dict)
        for hm in HashedMessage.objects.all():
            if   hm.dob_and_mobilephone_hash == j["dob_and_mobilephone_hash"] or \
                 hm.dob_and_email_hash == j["dob_and_email_hash"] or \
                 hm.email_and_mobilephone_hash == j["email_and_mobilephone_hash"] or \
                 hm.insurance_plan_and_insurance_member_hash == j["insurance_plan_and_insurance_member_hash"] or \
                 hm.mrn_and_node_hash == j["mrn_and_node_hash"]:

                for k, v  in update_dict.items():
                    setattr(hm, k, v)
                response['hm'] = model_to_dict(hm)                 
                hm.save()
        response['update_fields'] = update_keys
        return HttpResponse(json.dumps(response, indent=2),
                            content_type="application/json")
            
    return HttpResponse(json.dumps({"error":"This API requires and HTTP POST with a JSON object for content"}, indent=2),
                            content_type="application/json")

