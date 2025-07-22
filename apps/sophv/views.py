from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import DataElement, OID, MDN
from datetime import datetime
from django.contrib.auth.decorators import login_required
import csv


def convert_to_date(yyyymmdd):
    # convert datetime to date helper function
    date_obj = datetime.strptime(yyyymmdd, '%Y%m%d')
    return date_obj


@login_required
def sophv_index(request):
    return render(request, 'sophv/index.html', {})


def check_data_element_common_name(request, common_name, 
                                   message_type="hl7v2", 
                                   code=""):
    if request.GET.get("output_format"):
        output_format = request.GET.get("output_format")
    else:
        output_format = "json"
    mylist = []
    if not code:
        for i in DataElement.objects.filter(common_name=common_name):
            mylist.append(i.to_dict)


        if output_format == "csv":
            response = HttpResponse(content_type='text/csv')
            filename = "%s.csv" % common_name
            response['Content-Disposition'] = 'attachment; filename="%s"' %(filename)

            writer = csv.DictWriter(response, fieldnames=mylist[0].keys())
            # Write the header row
            writer.writeheader()

            # Write the data rows
            for row in mylist:
                writer.writerow(row)

            return response
        elif output_format == "json" or not output_format:
            return JsonResponse({"count": len(mylist), "codesets":mylist})

    else:
        
        if message_type == "hl7v2" or message_type == "csv":
            results = DataElement.objects.filter(common_name=common_name, 
                                             code=code)
            if len(results)>0:
                msg = "Code %s is valid for %s in a %s message." % (code, common_name, message_type)
                return JsonResponse({"status":"pass", "msg":msg})
            else:
                msg = "Code %s is invalid for %s in a %s message" % (code, common_name, message_type)
                return JsonResponse({"status":"fail", "msg":msg})

        elif message_type == "fhir":
            results = DataElement.objects.filter(common_name=common_name, 
                                             fhir_code=code)
            if len(results)>0:
                msg = "Code '%s' is valid for '%s' in a '%s' message." % (code, common_name, message_type)
                return JsonResponse({"status":"pass", "msg":msg})
            else:
                msg = "Code '%s' is invalid for '%s' in a '%s' message" % (code, common_name, message_type)
                return JsonResponse({"status":"fail", "msg":msg})
        else:
            msg = "Message type '%s' is invalid." % (message_type)
            return JsonResponse({"status":"fail", "msg":msg})
    return JsonResponse({"status":"fail", "msg":"No data found."})




@login_required
def mdn_index(request):
    mdns = MDN.objects.all()
    return render(request, 'sophv/mdn-index.html', {'mdns': mdns})




@login_required
def check_data_element_common_name(request, common_name, message_type, code):
    mdn = MDN.objects.get(common_name=common_name)
    response = {}
    if not message_type in ('hl7v2', 'csv', 'fhir','cda'):
        response['status'] = 'fail'
        response['message'] = f'Message type {message_type} is invalid'
        return JsonResponse(response)
    if message_type in ('hl7v2', 'csv', 'fhir', 'cda'):
        if mdn.data_element_type == 'text':
            try:
                str(code)
                response['status'] = 'pass'
                response['message'] = f'Code {code} is a valid code for {mdn.data_element_name}'
            except:
                response['status'] = 'fail'
                response['message'] = f'Code {code} is an invalid code for {mdn.data_element_name}'
        if mdn.data_element_type == 'numeric':
            try:
                float(code)
                response['status'] = 'pass'
                response['message'] = f'Code {code} is a valid numeric for {mdn.data_element_name}'
            except:
                response['status'] = 'fail'
                response['message'] = f'Code {code} is an invalid numeric for {mdn.data_element_name}'
        
        if mdn.data_element_type == 'date':
            try:
                convert_to_date(code)
                response['status'] = 'pass'
                response['message'] = f'Code {code} is a valid YYYYMMDD date for {mdn.data_element_name}'
            except ValueError:
                response['status'] = 'fail'
                response['message'] = f'Code {code} is an invalid code for {mdn.data_element_name}'

        if mdn.data_element_type == 'coded':
            print("here")
            filtered_oid = OID.objects.filter(oid=mdn.oid, code=code)
            
            
            if filtered_oid:
                response['status'] = 'pass'
                response['message'] = f'Code {code} is a valid code for {mdn.data_element_name}'
                response['details'] = mdn.to_dict()
            else:
                response['status'] = 'fail'
                response['message'] = f'Code {code} is an invalid code for {mdn.data_element_name}'
    return JsonResponse(response)


@login_required
def data_element_common_name(request, common_name):
    mdn = MDN.objects.get(common_name=common_name)
    return JsonResponse(mdn.to_dict())