from django.db import models
from ..report_metadata.models import HealthDataType, ProgramAreaType, PatientIDType
from oauth2_provider.models import Application
import uuid
from django.conf import settings
from django.urls import reverse
from .osdk_utils import sign_in
from foundry_sdk_runtime.types import ActionConfig, ActionMode, ValidationResult, ReturnEditsMode
__author__ = "Alan Viars"

class DataStream(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    description = models.TextField()
    allowable_payload_types = models.ManyToManyField(HealthDataType, 
                                        blank=True,
                                        related_name='allowable_payload_types')
    reviewers = models.ManyToManyField('auth.Group', related_name ='reviewers',
                                        blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

class TransactionType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.code


class Facility(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    url = models.URLField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"

    def __str__(self):
        return f'{self.code}-{self.name}'
    
    @property
    def npi(self):
        return self.code


    @property
    def facility_name(self):
        return self.name

    def save(self, *args, **kwargs):
        self.url = f"{settings.HOSTNAME_URL}/frontdoor/facility/{self.code}"
        super().save(*args, **kwargs)


class Origin(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, db_index=True)
    transaction_types = models.ManyToManyField(DataStream,  blank=True,
                                        related_name='data_streams')
    description = models.TextField()
    postal_code = models.CharField(max_length=10, blank=True)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, blank=True, null=True)
    url = models.URLField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.code
    
    @property
    def ori(self):
        return self.code
    

    @property
    def origin_name(self):
        return self.origin_name

    def save(self, *args, **kwargs):
        self.url = f"{settings.HOSTNAME_URL}/frontdoor/ori/{self.code}"
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "Agency ID"
        verbose_name_plural = "Agency IDs"
class Submitter(models.Model):
    origin = models.ForeignKey(Origin, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    application = models.ForeignKey(Application, on_delete=models.CASCADE,
                                    null=True, blank=True)
    transaction_types = models.ManyToManyField(TransactionType,  blank=True,
                                        related_name='submitter_tx_types')
    description = models.TextField()
    url = models.URLField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.origin.code}"
    
    @property
    def ori(self):
        return self.origin.code

    @property
    def submitter_name(self):
        return self.origin.name
    
    @property
    def submitter_code(self):
        return self.origin.code

    def save(self, *args, **kwargs):
        self.url = f"{settings.HOSTNAME_URL}/frontdoor/submitter/{self.origin.code}"
        super().save(*args, **kwargs)

class Destination(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, db_index=True)
    program_area = models.ManyToManyField(ProgramAreaType, blank=True, 
                                        related_name='program_area')
    description = models.TextField()
    url = models.URLField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)


    def __str__(self):
        return self.code

    @property
    def destination_name(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.url = f"{settings.HOSTNAME_URL}/frontdoor/destinations/{self.code}"
        super().save(*args, **kwargs)


INBOUND_TRANSACTION_TYPES = [
    ('REST-SUBMIT-API', 'Base Submission API'),
    ('FHIR-PROCESS-MESSAGE-API', 'FHIR Bundle Submission via process message endpoint.'),
    ('FILE-DROP', 'File/folder drop such as SFTP or AWS S3'),
    ('WEB-FORM', 'Front Door Web Forms'),
    ('EMAIL-ENCRYPTED', 'Encrypted Email'),
    ('EMAIL-DIRECT', 'Submitted using DIRECT Protocol')
]

class Submission(models.Model):
    submitter = models.ForeignKey(Submitter, on_delete=models.CASCADE, 
                            verbose_name="Origin Agency Identifier",
                            related_name='submitter_agency', blank=True, null=True, db_index=True)
    transaction_control_number = models.CharField(max_length=64, verbose_name="Transaction Control Number", 
                           db_index=True)
    transaction_control_reference = models.CharField(max_length=64, blank=True, null=True,
                            verbose_name="Transaction Control Reference",db_index=True, default = str(uuid.uuid4()))
    transaction_type = models.ForeignKey(TransactionType, 
                            on_delete=models.CASCADE, related_name='submission_tx_types')
    inbound_transmission_type = models.CharField(choices=INBOUND_TRANSACTION_TYPES, max_length=50, blank=True)
    origin  = models.ForeignKey(Origin, on_delete=models.CASCADE, verbose_name="Originating Agency Identifier",
                            related_name='originating_agency', blank=True, null=True, db_index=True)
    contributors = models.ManyToManyField(Origin, blank=True, related_name='contributors')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, blank=True, null=True)
    destination_tcn = models.CharField(max_length=100, blank=True, verbose_name="Destination Transaction Control Number", 
                                       default=uuid.uuid4,
                                       help_text="The server's tranaction control number, generated automatically.")
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, blank=True, null=True, related_name='facility')
    facility_code = models.CharField(max_length=100, blank=True, null=True)
    facility_postal_code = models.CharField(max_length=10, blank=True)
    subject_postal_code = models.CharField(max_length=10, blank=True)
    status_url = models.URLField(blank=True, default='')
    status = models.CharField(max_length=20, blank=True, choices=[('PENDING', 'PENDING'), ('REJECTED', 'REJECTED'), ('ACCEPTED', 'ACCEPTED')])
    onecdc_status = models.CharField(max_length=20, blank=True, default="")
    onecdc_submitted = models.BooleanField(default=False)
    onecdc_response = models.TextField(blank=True) 
    inbound_source_type = models.CharField(max_length=120, blank=True, 
                                           choices=INBOUND_TRANSACTION_TYPES, default="REST-SUBMIT-API")
    payload_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE)
    person_id = models.CharField(max_length=100, blank=True)
    person_id_issuer = models.CharField(max_length=100, blank=True)
    person_id_type = models.ForeignKey(PatientIDType, blank=True, null=True, on_delete=models.CASCADE)
    metadata_json = models.TextField(blank=True)
    metadata_file = models.FileField(upload_to='uploads/metadata/', blank=True)
    payload_txt = models.TextField(blank=True)
    payload_bin = models.BinaryField(blank=True)
    payload_file = models.FileField(upload_to='uploads/payloads/', blank=True)
    payload_hash = models.CharField(max_length=100, blank=True, db_index=True)
    unique_payload = models.BooleanField(default=True)
    payload_server_reference = models.CharField(max_length=100, blank=True)
    hl7_parsed_message_json = models.TextField(blank=True)
    fhir_bundle_json = models.TextField(blank=True)
    response_json = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_control_number}"
    
    @property
    def submitter_code(self):
        return self.submitter.origin.code

    @property
    def origin_code(self):
        return self.origin.code
    
    @property
    def destination_code(self):
        return self.destination.code
    
    @property
    def contributor_codes(self):
        return [c.code for c in self.contributors.all()]
    @property
    def contributor_codes_pipe_delimited(self):
        joined = "".join([f"{c.code}|" for c in self.contributors.all()])
        # strip off the ending |
        if joined.endswith("|"):
            joined = joined[:-1]
        # if there are no contributors, return an empty string
        if not joined:
            return ""
        return joined

    @property
    def payload_reference(self):
        return self.payload_file.url

    @property
    def payload_file_text(self):
        opened_file = open(self.payload_file.path, 'r')
        file_text = opened_file.read()
        opened_file.close()
        return file_text
    
    @property
    def submit_to_1cdp(self):
        if self.onecdc_submitted == False and self.status == "ACCEPTED":
            # upload to 1CDP
            print("Submitting to 1CDP")
           

            print(self.transaction_control_number)
            client = sign_in()
            response = client.ontology.actions.create_cdcspec_submissions(
                                action_config=ActionConfig(mode=ActionMode.VALIDATE_AND_EXECUTE,
                        return_edits=ReturnEditsMode.ALL),
                transaction_control_number =int(self.transaction_control_number), 
                transaction_control_reference=self.transaction_control_reference,
                status=self.status, 
                originating_agency_identifer=str(self.origin), 
                destination_agency_identifier=str(self.destination), 
                submitter_agency_identifier=str(self.submitter), 
                transaction_type=str(self.transaction_type), 
                contributing_agency_identifiers=str(self.contributor_codes_pipe_delimited),
                unique_payload=self.unique_payload, 
                facility=int(self.facility.code), 
                facility_postal_code=int(self.facility_postal_code), 
                subject_postal_code=int(self.subject_postal_code),
                inbound_source_type=self.inbound_source_type, 
                payload_type=str(self.payload_type),
                person_id=self.person_id, 
                person_id_issuer=self.person_id_issuer,
                person_id_type=str(self.person_id_type),
                payload_hash=self.payload_hash, 
                hl7v2_payload=self.hl7_parsed_message_json, 
                fhirbundle_payload=self.fhir_bundle_json, 
                payload_file=self.payload_file_text, 
                date_created=str(self.date_created), 
                date_updated=str(self.date_updated))
    
            # Check if the validation was successful
            print("VALIDATION", response.validation)
            if response.validation.validation_result == ValidationResult.VALID:
                print(response.edits)
                self.onecdc_response = str(response.edits)
                self.onecdc_submitted = True
                self.save()


    @property
    def as_dict(self):
        d= {"transaction_control_number": self.transaction_control_number,
            "transaction_control_reference": self.transaction_control_reference,
            "status": self.status,
            "originating_agency_identifer": self.origin.code,
            "destination_agency_identifier": self.destination.code,
            "submitter_agency_identifier": self.submitter.origin.code,
            "transaction_type": self.transaction_type.code,
            "contributing_agency_identifiers": self.contributor_codes_pipe_delimited,
            'unique_payload' :self.unique_payload,
            "facility": self.facility.code,
            "facility_postal_code": self.facility_postal_code,
            "subject_postal_code": self.subject_postal_code,
            "inbound_source_type": self.inbound_source_type,
            "payload_type": self.payload_type.code,
            "person_id": self.person_id,
            "person_id_issuer": self.person_id_issuer,
            "person_id_type": self.person_id_type.code,
            "payload_hash": self.payload_hash,
            'hl7v2_payload':self.hl7_parsed_message_json,
            'fhirbundle_payload': self.fhir_bundle_json,
            'payload_file': self.payload_file_text,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
            }
        return d
    @property
    def as_dict_response(self):
        d = self.as_dict
        d["onecdc_submitted"]= self.onecdc_submitted,
        d["transaction_control_number"] = self.transaction_control_reference
        d["transaction_control_reference"] = self.transaction_control_number
        return d


    def save(self, *args, **kwargs):
        self.transaction_control_reference = str(uuid.uuid4())
        reverse_url = reverse('frontdoor:view_submission', args= (self.transaction_control_number, ))   
        self.transaction_control_reference = str(uuid.uuid4())
        self.status_url = f"{settings.HOSTNAME_URL}{reverse_url}"
        super().save(*args, **kwargs)

STATUS_TYPES = [
    ('PENDING', 'PENDING'),
    ('REJECTED', 'REJECTED'),
    ('ACCEPTED', 'ACCEPTED')
]
class SubmissionReceipt(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_TYPES)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    class Meta:
        verbose_name = "Receipts"
        verbose_name_plural = "Receipts"

    def __str__(self):
        return f"{self.submission}-{self.status}"
    
    @property
    def as_receipt_dict(self):
        return {"transaction_control_number": self.submission.destination_tcn,
                "transaction_control_reference": self.submission.submitter_tcn,
                "status": self.status,
                "date_created": str(self.date_created),
                "date_updated": str(self.date_updated)}


    @property
    def submitter_code(self):
        return self.submission.submitter.origin.code