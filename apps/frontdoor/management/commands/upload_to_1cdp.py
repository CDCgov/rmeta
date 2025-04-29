from cdc_submission_spec_api_sdk import FoundryClient
from foundry_sdk_runtime.auth import ConfidentialClientAuth
import os
from osdk_connection_read_write_sdk.ontology.objects import VocabularyOption2ValueSetAllVersions
from foundry_sdk_runtime.errors.palantir_rpc_exception import PalantirRPCException
from foundry_sdk_runtime.types import ActionConfig, ActionMode, ValidationResult, ReturnEditsMode
from datetime import date
from django.core.management.base import BaseCommand
from ...models import Submission
import json

ONECDP_SUBMISSION_API_CLIENT_ID =    os.getenv("ONECDP_SUBMISSION_API_CLIENT_ID", '<fill in CLIENT_ID>')
ONECDP_SUBMISSION_API_CLIENT_SECRET= os.getenv("ONECDP_SUBMISSION_API_CLIENT_SECRET", '<fill in CLIENT_SECRET>')



auth = ConfidentialClientAuth(

    client_id=ONECDP_SUBMISSION_API_CLIENT_ID,
    client_secret=ONECDP_SUBMISSION_API_CLIENT_SECRET,
    hostname="https://1cdp.cdc.gov",
    should_refresh=True,
)

auth.sign_in_as_service_user()

client = FoundryClient(auth=auth, hostname="https://1cdp.cdc.gov")

def sign_in():
    
    auth = ConfidentialClientAuth(
        client_id=ONECDP_SUBMISSION_API_CLIENT_ID,
        client_secret=ONECDP_SUBMISSION_API_CLIENT_SECRET,
        hostname="https://1cdp.cdc.gov",
        should_refresh=True)
    auth.sign_in_as_service_user()
    client = FoundryClient(auth=auth, hostname="https://1cdp.cdc.gov")
    return client

def upload_to_1cdp(client, transaction_control_number=None):
    if not transaction_control_number:
        submissions = Submission.objects.filter(status="ACCEPTED", onecdc_submitted = False)
    else: 
        submissions = Submission.objects.filter(transaction_control_number=transaction_control_number)
    for submission in submissions:
            print(submission.transaction_control_number)
            transaction_control_number = submission.transaction_control_number
    
    
            response = client.ontology.actions.create_cdcspec_submissions(
                        action_config=ActionConfig(mode=ActionMode.VALIDATE_AND_EXECUTE,
                        return_edits=ReturnEditsMode.ALL),
                transaction_control_number =int(submission.transaction_control_number), 
                transaction_control_reference=submission.transaction_control_reference,
                status=submission.status, 
                originating_agency_identifer=str(submission.origin), 
                destination_agency_identifier=str(submission.destination), 
                submitter_agency_identifier=str(submission.submitter), 
                transaction_type=str(submission.transaction_type), 
                contributing_agency_identifiers=str(submission.contributor_codes_pipe_delimited),
                unique_payload=submission.unique_payload, 
                facility=int(submission.facility.code), 
                facility_postal_code=int(submission.facility_postal_code), 
                subject_postal_code=int(submission.subject_postal_code),
                inbound_source_type=submission.inbound_source_type, 
                payload_type=str(submission.payload_type),
                person_id=submission.person_id, 
                person_id_issuer=submission.person_id_issuer,
                person_id_type=str(submission.person_id_type),
                payload_hash=submission.payload_hash, 
                hl7v2_payload=submission.hl7_parsed_message_json, 
                fhirbundle_payload=submission.fhir_bundle_json, 
                payload_file=submission.payload_file_text, 
                date_created=str(submission.date_created), 
                date_updated=str(submission.date_updated))
            # Check if the validation was successful
            print("VALIDATION", response.validation)
            if response.validation.validation_result == ValidationResult.VALID:
                print(response.edits)
                submission.onecdc_response = str(response.edits)
                submission.onecdc_submitted = True
                submission.save()



class Command(BaseCommand):
    help = "Submit Transaction to 1CDP Front Door"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            '--transaction_control_number',  # Name for command-line
            type=int,  # Type of data
            help='Transaction Control Number', # Help text
            default=None,  # Default value if not provided
        )


    def handle(self, *args, **options):
        client = sign_in()
        upload_to_1cdp(client, options['transaction_control_number'])

