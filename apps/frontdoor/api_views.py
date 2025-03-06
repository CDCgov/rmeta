from .models import Submission
import logging
import hashlib
from django.conf import settings
from oauth2_provider.decorators import protected_resource
from django.http import JsonResponse
from .utils import (check_origin, check_submitter, check_destination, check_json, 
                    check_transaction_type, check_health_data_type, check_facility, 
                    check_payload_hash_exists, submit_to_1cdp)
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import FileFieldForm, FileFieldForm2
import json
from .management.commands.parsehl7 import parse_message, invalid_hl7
from .models import TransactionType, HealthDataType, Origin, Destination, Submitter, Facility, Submission
from django.urls import reverse


def api_home(request):
    submission_url = reverse('frontdoor:restful_singleton_submission')
    msg = f"""Send a POST request to {submission_url} with two files."""
    curl_example = f"""curl -H "Authorization: Bearer <REPLACE WITH YOUR ACCESS TOKEN>" -F "metadata_file=@metadata_file.json" -F "payload_file=@payload_file.json" {settings.HOSTNAME_URL}{submission_url}"""

    return JsonResponse({'status': 'ok',
                         'message': msg,
                         'curl_example': curl_example})

#@require_POST
@csrf_exempt
def restful_submission(request):
    if request.method == 'POST':
        print("hello")
        form = FileFieldForm(request.POST, request.FILES)
        print("world")
        #print(form)
        cleaned_data = form.clean
        print(dir(cleaned_data))
        files = cleaned_data
        for f in files:
            print(f)
        if form.is_valid():
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'fail', 'message': form.errors})
    # get files via post
    #file_data = request.body
    # Extract filename from request headers, if available
    #filename = request.headers.get('Content-Disposition', '').split('filename=')[-1].strip('"')    
    #if not filename:
    #    filename = 'default_filename.txt'

    #print(filename, file_data)
    # get headers
    headers = request.headers
    # get user
    #user = get_user(request)
    
    #print(files, post_data, headers)

    #metadata_file = files.get('metadata_file')
    #payload_file = files.get('payload_file')
    #print( metadata_file, payload_file)
    errors = check_json("{}")
    if errors:
        return JsonResponse({'status': 'fail', 'message': errors})



    # check if destination exists
    destination = check_destination(post_data.get('destination'))
    if not destination:
        msg = "Invalid destination. Your submission's trancation control number was not registered."
        return JsonResponse({'status': 'fail', 
                             'message': msg})
    # check if origin exists
    origin = check_origin(post_data.get('origin'))
    if not origin:
        return JsonResponse({'status': 'fail', 'message': 'Invalid origin'})
    # check if submitter exists
    submitter = check_submitter(post_data.get('submitter'))
    if not submitter:
        return JsonResponse({'status': 'fail', 'message': 'Invalid submitter'})


    return JsonResponse({'status': 'ok'})


def view_submission(request, transaction_control_number):
    try:
        submission = Submission.objects.get(transaction_control_number=transaction_control_number)
    except Submission.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Submission not found.'})
    return JsonResponse({'status': 'ok', 'response': submission.as_dict})

@csrf_exempt
def restful_singleton_submission(request):
    inbound_transmission_type = 'REST-SUBMIT-API'
    duplicate_payload = False
    if request.method == 'POST':
        metadata_file = None
        payload_file = None
        form = FileFieldForm2(request.POST, request.FILES)
        if form.is_valid():
            warnings = []
            errors = []
            metadata_file = form.cleaned_data['metadata_field']
            payload_file = form.cleaned_data['payload_field']
            if not metadata_file:

                return JsonResponse({'status': 'fail', 
                                     'message': 'metadata file was not found. Submission metadata is required on this endpoint.'}) 
            if not payload_file:
                return JsonResponse({'status': 'fail', 'message': 'Payload file was not found. Payload is required on this endpoint.'}) 
            metadata_file = metadata_file[0]
            payload_file = payload_file[0]
            # print("METADATA FILE", metadata_file, metadata_file.size, dir(metadata_file))
            # print("PAYLOAD FILE", payload_file, payload_file.size)

            metadata_file_path = f'./uploads/submissions/{metadata_file.name}'
            payload_file_path = f'./uploads/payloads/{payload_file.name}'
            metadata_json = None
            
            with open(metadata_file_path, 'wb+') as file:
                file.write(metadata_file.read())

            with open(payload_file_path, 'wb+') as file:
                file.write(payload_file.read())

            with open(metadata_file_path, 'r') as fh:
                metadata_json = fh.read()

            # get the hash of the payload.
            payload_hash = ''
            with open(payload_file_path, 'r', encoding='utf-8') as fh:
                payload_bin = fh.read()
                hash_object = hashlib.sha1(payload_bin.encode('utf-8'))
                hex_dig = hash_object.hexdigest()
                payload_hash=hex_dig
            if check_payload_hash_exists(payload_hash):
                msg = f'Payload with identical hash {payload_hash} has already been submitted.  This appears to be a duplicate.'
                duplicate_payload = True
                warnings.append(msg)

            # check if the metadata file is a valid json
            jserrors = check_json(metadata_json)
            if jserrors:
                errors.append(jserrors)
                return JsonResponse({'status': 'fail', 'errors': errors, 'wanings': warnings})
            
            # its valid so load it into a dict.
            metadata_json = json.loads(metadata_json)


            # check if valid transaction type
            transaction_type = metadata_json.get('transaction_type')
            if not transaction_type:
                return JsonResponse({'status': 'fail', 'message': 'Transaction type is required.'})
            if not check_transaction_type(transaction_type):
                return JsonResponse({'status': 'fail', 'message': f'Invalid transaction type {transaction_type}.'})
            
            
            # check if the health data type exists
            health_data_type = metadata_json.get('health_data_type')
            if not health_data_type:
                msg = 'Health data type is required.'
                errors.append(msg)
                return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})
            if not check_health_data_type(health_data_type):
                msg = f'Invalid health data type {health_data_type}.'
                errors.append(msg)
                return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})

           # check if the tcn exists
            tcn = metadata_json.get('transaction_control_number')
        
            if not tcn:
                msg = 'Transaction control number is required'
                errors.append(msg)
                return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})

            #check tcn has not already been used:
            
            if Submission.objects.filter(transaction_control_number=tcn).exists():
                msg = f'transaction_control_number {tcn} has already been used.'
                if settings.REQUIRE_UNIQUE_TRANSACTION_CONTROL_NUMBERS:
                    errors.append(msg)
                    return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})

                else:
                        warnings.append(msg) 
           # check if the tcr exists, it it exists, it must reference a valid transaction_control_number
            tcr = metadata_json.get('transaction_control_reference')
            if not tcr:
                pass
            else:
                if not Submission.objects.filter(transaction_control_number=tcr).exists():
                    msg = f'transaction_control_reference {tcr} does not reference a valid transaction_control_number.'
                    errors.append(msg)
                    return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})


            # check if the origin exists
            originating_agency_identifier = metadata_json.get('originating_agency_identifier')
            origin = check_origin(originating_agency_identifier)
            if not origin:
                ori = originating_agency_identifier
                msg = f'Invalid origin {ori}'
                errors.append(msg)
                return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})

           
            # check if contributing agencies exist
            contributing_agency_identifiers = metadata_json.get('contributing_agency_identifiers',[])
            cris = []
            for agency in contributing_agency_identifiers:
                cri = check_origin(agency)
                if check_origin(cri):
                    cris.append(cri)
                else:
                    msg = f'Invalid contributing agency identifer {agency}.'
                    errors.append(msg)
                    return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})


 
            # check if the destination exists
            destination = check_destination(metadata_json.get('destination_agency_identifier'))
            if not destination:
                dai = metadata_json.get('destination_agency_identifier')
                msg = f'Invalid destination {dai}.'
                errors.append(msg)
                return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})


            # check if the submitter exists
            submission_agency_identifier = check_submitter(metadata_json.get('submitting_agency_identifier'))
            if not submission_agency_identifier:
                sai = metadata_json.get('submitting_agency_identifier')
                msg = f'Invalid submitter {sai}.'
                errors.append(msg)
                return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})

            # check if the submitter exists
            submission_agency_identifier = check_submitter(metadata_json.get('submitting_agency_identifier'))
            if not submission_agency_identifier:
                sai = metadata_json.get('submitting_agency_identifier')
                return JsonResponse({'status': 'fail', 'message': f'Invalid submitter {sai}.'})   

            #check if person_id is present
            person_id = metadata_json.get('person_id','')
            if not person_id:
                
                if settings.REQUIRE_PERSON_ID:
                    msg = 'Person ID is required.'
                    errors.append(msg)
                    return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})
                else:
                    msg = 'Person ID is not present. Person ID should be provided with each subject record.'
                    warnings.append(msg)
                
            # check if person_id_issuer is presentpresent
            person_id_issuer = metadata_json.get('person_id_issuer','')
            if not person_id_issuer:
                
                if settings.REQUIRE_PERSON_ID_ISSUER:
                    msg = 'Person ID issuer is required.'
                    errors.append(msg)
                    return JsonResponse({'status': 'fail', 'errors': errors, 'warnings':warnings})
                else:
                    msg = 'Person ID issuer is not present. Person ID issuer should be provided with each subject record.'
                    warnings.append(msg)
            
            # check if the facility exists
            facility_code = metadata_json.get('facility_code','')
            if not facility_code:
                if settings.REQUIRE_FACILITY_CODE:
                    return JsonResponse({'status': 'fail', 'message': 'Facility code is required.'})
                else:
                    warnings.append('Facility code is not present. Facility code should should be provided with each subject record.')
            else:
                if not check_facility(facility_code):
                    warnings.append(f'Facility code {facility_code} is not a valid.')
            
            subject_postal_code = metadata_json.get('subject_postal_code','')
            if not subject_postal_code:
                warnings.append('Subject postal code is not present. Subject postal code should be provided with each subject record.')
            facility_postal_code = metadata_json.get('facility_postal_code','')
            if not facility_postal_code:
                warnings.append('Facility postal code is not present. Facility postal code should be provided with each subject record.')

            # handle hl7v2 message
            hl7_message = ''
            if health_data_type == 'HL7V2':
                hl7_errors = invalid_hl7(payload_file_path)
                if hl7_errors:
                    msg = 'Invalid HL7 message.'
                    errors.append(msg)
                    return JsonResponse({'status': 'fail', 'errors': errors})
                else:
                    hl7_message =parse_message(payload_file_path)[0]
                    hl7_facility_code = hl7_message['message'].get('from_location')
                    if facility_code != hl7_facility_code:
                        warnings.append(f'Facility code {facility_code} does not match the facility code in the HL7 message {hl7_facility_code}.')
                    if not facility_code:
                        facility_code=hl7_facility_code

            # grab the facility object if it exists?
            if facility_code:
                facility = Facility.objects.get(code=facility_code)
                fc = facility.code
            else:
                fc = ''
                facility=None

            # create a new submission using the values above
            submission = Submission.objects.create(
                transaction_control_number=tcn,
                transaction_control_reference=tcr,
                inbound_transmission_type=inbound_transmission_type,
                transaction_type=TransactionType.objects.get(code=transaction_type),
                payload_type=HealthDataType.objects.get(code=health_data_type),
                origin=Origin.objects.get(code=originating_agency_identifier),
                destination=Destination.objects.get(code=destination),
                submitter=Submitter.objects.get(origin__code=submission_agency_identifier),
                facility=facility,
                facility_code=facility_code,
                person_id=person_id,
                person_id_issuer=person_id_issuer,
                subject_postal_code=subject_postal_code,
                facility_postal_code=facility_postal_code,
                metadata_file=metadata_file_path,
                payload_file=payload_file_path,
                payload_hash=payload_hash,
                duplicate_payload=duplicate_payload,
                metadata_json=json.dumps(metadata_json, indent=2),
                hl7_parsed_message_json=json.dumps(hl7_message, indent=2)
            )   
            submission.contributors.set(cris)
            submission.save()

            # Submit to 1CDP
            submit_to_1cdp(submission)




            return JsonResponse({'status': 'ok', 'repsonse': submission.as_dict, 'warnings': warnings,
                                 'errors': errors})
        else:
            return JsonResponse({'status': 'fail', 'message': form.errors})
    return JsonResponse({'status': 'fail', 'message': 'Only POST method is allowed'})


