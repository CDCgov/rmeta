from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import DataElement
import csv
author__ = "Alan Viars"

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