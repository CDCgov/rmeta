from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import AnonymizedMessage
import json
from django.core.serializers.json import DjangoJSONEncoder
from ..hashcow.helpers import kickout_400
import sys
from datetime import date
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def anonymize(request):
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
        dbfields = [f.name for f in AnonymizedMessage._meta.get_fields()]
        for field in dbfields:
            # print(field)
            if "date" in field and "updated" not in field:
                print(field)
                if j[field]:
                    year = int(j[field][0:4])
                    month = int(j[field][5:7])
                    day = int(j[field][9:10])
                    print(year, month, day)
                    j[field]=date(year, month, day)
        
        #del j['id']
        #del j['hashlink']
        update_dict = {}
        update_keys = []
        for k,v in j.items():
            if v:
                update_dict[k]=j[k]
                update_keys.append(k)
        save_to_hm = None

        am = AnonymizedMessage.objects.create(**j)

        #print(update_dict)
        #for am in AnonymizedMessage.objects.all():
        #    if   am.dob_and_mobilephone_hash == j["dob_and_mobilephone_hash"] or \
        #         am.dob_and_email_hash == j["dob_and_email_hash"] or \
        #         am.email_and_mobilephone_hash == j["email_and_mobilephone_hash"] or \
        #         am.insurance_plan_and_insurance_member_hash == j["insurance_plan_and_insurance_member_hash"] or \
        #         am.mrn_and_node_hash == j["mrn_and_node_hash"]:

        #        for k, v  in update_dict.items():
        #            setattr(am, k, v)
        #        response['am'] = model_to_dict(am)                 
        #        am.save()
        #response['update_fields'] = update_keys
        return HttpResponse(json.dumps(am.to_anon_dict, cls=DjangoJSONEncoder,indent=2),
                            content_type="application/json")
            
    return HttpResponse(json.dumps({"error":"This API requires and HTTP POST with a JSON object for content"}, indent=2),
                            content_type="application/json")