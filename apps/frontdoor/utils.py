from .models import Origin, Submitter, Destination, Facility, TransactionType, Submission
import json
from ..report_metadata.models import HealthDataType, PatientIDType


def hl7_lab_sanity_check(message):
    "return a list of errors if any"
    errors = []
    #print(dum)
    if not message:
        errors.append("Empty message.")
    return errors


def check_json(document):
    "Check if the initial document is a valid JSON object"
    try:
        djson = json.loads(document)
        if not isinstance(djson, type({})):
            return 'Not a JSON object (i.e. {} )'
    except ValueError:
            return 'Invalid JSON.'
    return ""


def get_user(request):
    "Get the resource owner or the logged-in user"
    try:
        user = request.resource_owner
    except AttributeError:
        user = request.user
    return user

def check_facility(facility_code):
    "Check if the facility exists"
    try:
        facility = Facility.objects.get(code=facility_code)
    except Facility.DoesNotExist:
        return False
    return facility

def check_payload_hash_exists(payload_hash):
    "Check if the payload hash exists"    
    return Submission.objects.filter(payload_hash=payload_hash).exists()

    


def check_submission(tcn):
    "Check if the submission exists"
    try:
        submission = Submission.objects.get(transaction_control_number=tcn)
    except Submission.DoesNotExist:
        return False

def check_transaction_type(transaction_type_code):
    "Check if the transaction type exists"
    
    try:
        transaction_type = TransactionType.objects.get(code=transaction_type_code)
    except TransactionType.DoesNotExist:
        return False
    return transaction_type

def check_health_data_type(health_data_type_code):
    "Check if the health data type exists"
    try:
        health_data_type = HealthDataType.objects.get(code=health_data_type_code)
    except HealthDataType.DoesNotExist:
        return False
    return health_data_type

def check_person_id_type(person_id_type):
    "Check if the health data type exists"
    try:
        person_id_type = PatientIDType.objects.get(code=person_id_type)
    except PatientIDType.DoesNotExist:
        return False
    return person_id_type

def check_origin(origin_code):
    "Check if the origin exists"
    try:
        origin = Origin.objects.get(code=origin_code)
    except Origin.DoesNotExist:
        return False
    return origin

def check_submitter(submitter_code):
    "Check if the submitter exists"
    try:
        submitter = Submitter.objects.get(origin__code=submitter_code)
    except Submitter.DoesNotExist:
        return False
    return submitter

def check_destination(destination_code):
    "Check if the destination exists"
    try:
        destination = Destination.objects.get(code=destination_code)
    except Destination.DoesNotExist:
        return False
    return destination



