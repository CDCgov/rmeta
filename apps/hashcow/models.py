from django.db import models
from django.forms.models import model_to_dict
from localflavor.us.models import USPostalCodeField
import uuid
from localflavor.us.us_states import USPS_CHOICES

CASE_STATUS_CHOICES = (('SUSPECTED','SUSPECTED'),('PROBABLE','PROBABLE'),
                       ('CONFIRMED','CONFIRMED'))

class HashedMessage(models.Model):
    hashlink = models.CharField(max_length=36, default=uuid.uuid4,
                             unique=True, db_index=True)
    
    # Hashes
    dob_and_mobilephone_hash = models.CharField(max_length=64, blank=True, default='',)
    email_and_mobilephone_hash = models.CharField(max_length=64, blank=True, default='')
    dob_and_email_hash = models.CharField(max_length=64, blank=True, default='')
    dob_and_fn_and_ln_hash = models.CharField(max_length=64, blank=True, default='',)
    insurance_plan_and_insurance_member_hash = models.CharField(max_length=64, blank=True, default='')
    mrn_and_node_hash = models.CharField(max_length=64, blank=True, default='')

    # Optional but strongly reccomended transaction metadata - should enforce some of this in pilots.
    initial_message_id = models.CharField(max_length=36, default='', blank=True,
                             db_index=True,
                             help_text="Link to the initial message_id for a given case/person.")
    encompassing_encounter_id = models.CharField(max_length=64, default='', blank=True,
                             db_index=True,
                             help_text="Link to the initial message_id for a given case/person.")
    source_system_case_report_type = models.CharField(max_length=15, default='', blank=True, 
                                           db_index=True, choices=CASE_STATUS_CHOICES)
    source_system = models.CharField(max_length=36, blank=True, default='')
    cdc_receiving_system = models.CharField(max_length=36, blank=True, default='')
    report_url = models.URLField(max_length=512, blank=True, default='')
    reportable_condition_flag = models.BooleanField(default=False, null=True)
    notifiable_condition_flag = models.BooleanField(default=False, null=True)
    current_case_status = models.CharField(max_length=15, default='', blank=True, 
                                           db_index=True, choices=CASE_STATUS_CHOICES)
    final_case_status = models.CharField(max_length=15, default='', blank=True, 
                                         db_index=True, choices=CASE_STATUS_CHOICES)
    final_case_status_date = models.DateField(blank=True, null=True)
    
    # Source System Metadata
    source_system_node = models.CharField(max_length=36, blank=True)
    source_system_transaction_id = models.CharField(max_length=36, blank=True, default='')
    source_system_initial_case_report_id = models.CharField(max_length=36, blank=True, default='')
    source_system_case_report_link_id = models.CharField(max_length=36, blank=True, default='')
    source_systems_patient_id_issuer = models.CharField(max_length=36, blank=True, default='')
    source_data_format = models.CharField(max_length=36, blank=True, default='')
    source_data_transport_type = models.CharField(max_length=36, blank=True, default='')
    
    # Core test data...just the highlights please
    test_ordered_test_loinc_code = models.CharField(max_length=36, blank=True, default='')
    test_ordered_test_device_identifier = models.CharField(max_length=36, blank=True, default='')
    test_ordered_result_loinc_code= models.CharField(max_length=36, blank=True, default='')
    test_ordered_snomed_code = models.CharField(max_length=36, blank=True, default='')
    test_ordered_result_date = models.DateField(blank=True, null=True)
    test_ordered_accession_num_or_specimen_id = models.CharField(max_length=36, blank=True, default='')
    
    # CDC Recipient System Metadata
    cdc_receiving_system_status = models.CharField(max_length=36, blank=True, default='')
    cdc_receiving_system_url = models.URLField(max_length=512, blank=True, null=True)

    # Truncated Patient Data. Name, DOB, and other identifiers removing names and other PII
    patient_age = models.PositiveSmallIntegerField(blank=True, default=0)
    patient_race = models.CharField(max_length=36, blank=True, default='')
    patient_ethnicity = models.CharField(max_length=36, blank=True, default='')
    patient_sex = models.CharField(max_length=36, blank=True, default='')
    patient_address_state = USPostalCodeField(blank=True, default='', choices=USPS_CHOICES)
    patient_residence_zip_code= models.CharField(max_length=36, blank=True, default='')
    patient_residence_county = models.CharField(max_length=128, blank=True, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    sanitized_payload = models.TextField(blank=True, default='{}')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, commit=True, **kwargs):
        if commit:
            super(HashedMessage, self).save(**kwargs)


    def __str__(self):
        return "%s" % (self.hashlink)

    class Meta:
        verbose_name_plural = 'Hashed Messages'
        verbose_name = 'Hashed Message'


    @property
    def dob_mobile(self):
        if not self.dob_and_mobilephone_hash:
            return ""
        return "%s..." % (self.dob_and_mobilephone_hash[0:5])
    @property
    def dob_email(self):
        if not self.dob_and_email_hash:
            return ""
        return "%s..." % (self.dob_and_email_hash[0:5])
    @property
    def email_mobile(self):
        if not self.email_and_mobilephone_hash:
            return ""
        return "%s..." % (self.email_and_mobilephone_hash[0:5])
    @property
    def mrn_node(self):
        if not self.mrn_and_node_hash:
            return ""
        return "%s..." % (self.mrn_and_node_hash[0:5])
    @property
    def ins_plan_member(self):
        if not self.insurance_plan_and_insurance_member_hash:
            return ""
        return "%s..." % (self.insurance_plan_and_insurance_member_hash[0:5])


    @property
    def is_initial_message(self):
        if self.initial_message_id:
            return False
        return True
    
    @property
    def as_dict(self):
        return  {}
