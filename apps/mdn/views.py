from django.shortcuts import render
from ..sophv.models import MDN, OID
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required



def convert_to_date(yyyymmdd):
    date_obj = datetime.strptime(yyyymmdd, '%Y%m%d')
    return date_obj

@login_required
def index(request):
    mdns = MDN.objects.all()
    return render(request, 'mdn/index.html', {'mdns': mdns})


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