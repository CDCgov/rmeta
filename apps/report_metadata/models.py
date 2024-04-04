from django.db import models
import uuid
import json
import bcrypt
from localflavor.us.models import USPostalCodeField, USSocialSecurityNumberField, USZipCodeField
from slugify import slugify
from localflavor.us.us_states import USPS_CHOICES
from django.conf import settings

CASE_STATUS_CHOICES = (('SUSPECTED','SUSPECTED'),('PROBABLE','PROBABLE'),
                       ('CONFIRMED','CONFIRMED'))


class PersonHashType(models.Model):
    code = models.CharField(max_length=255, default='', blank=True, unique=True)
    name = models.CharField(max_length=255, default='', blank=True)
    pepper_prefix = models.CharField(max_length=255, default='', blank=True,
                    help_text="Prepend this text to the value to be hashed.")
    series = models.SmallIntegerField(default=0)
    bcrypt_salt = models.CharField(max_length=64, default='', blank=True)
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Types: People Hashes'
        verbose_name = 'Types: Person Hash'

    @property
    def prefix(self):
        return "%s^%s" % (self.pepper_prefix, self.series)


    @property
    def salt(self):
        return "%s..." % (self.bcrypt_salt[7:11])
    


    def save(self, commit=True, **kwargs):
        if commit:
            if not self.bcrypt_salt:
                salt = bcrypt.gensalt(settings.BCRYPT_ROUNDS)
                self.bcrypt_salt =  salt.decode()
                self.series += 1

            if not self.code:
                self.name = self.pepper_prefix
                self.code = "%s" %  (self.pepper_prefix)
                self.code = self.code.upper()

            super(PersonHashType, self).save(**kwargs)


    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name,
                 "prefix": self.prefix,
                "description": self.description,
                "updated": str(self.updated)}


class AnonyomizedDataNeed(models.Model):
    code = models.CharField(max_length=255, default='', unique=True)
    name = models.CharField(max_length=255, default='')
    keep = models.BooleanField(blank=True, default=False)
    hipaa_id = models.BooleanField(blank=True, default=False)
    in_syndromic_message = models.BooleanField(blank=True, default=False)
    pprl_hash = models.BooleanField(blank=True, default=False)
    eicr_version = models.CharField(max_length=16, default='', blank=True)
    eicr_data_element = models.CharField(max_length=255, default='', blank=True)
    eicr_template = models.CharField(max_length=255, default='', blank=True)
    eicr_xpath = models.CharField(max_length=512, default='', blank=True)
    fhir_resource_version = models.CharField(max_length=512, default='', blank=True)
    fhir_resource_type = models.CharField(max_length=512, default='', blank=True)
    fhir_resource_path = models.CharField(max_length=512, default='', blank=True)
    hl7v2_version  = models.CharField(max_length=512, default='', blank=True)
    hl7v2_path  = models.CharField(max_length=512, default='', blank=True)
    other_path = models.CharField(max_length=512, default='', blank=True)
    other_url=  models.CharField(max_length=512, default='', blank=True)
    message_field_name = models.CharField(max_length=512, default='', blank=True)
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Anonyomized Data Needs'
        verbose_name = 'Anonyomized Data Need'

    @property
    def as_dict(self):
        return  {"code":self.code, "name": self.name, 
                 "keep":self.keep, 
                "hipaa_id": self.hipaa_id,
                "in_syndromic_message": self.in_syndromic_message, 
                "pprl_hash": self.pprl_hash, 
                "eicr_version": self.eicr_version, 
                "eicr_data_element": self.eicr_data_element, 
                "eicr_template": self.eicr_template,
                "eicr_xpath": self.eicr_xpath,
                "fhir_resource_version": self.fhir_resource_version, 
                "fhir_resource_type": self.fhir_resource_type, 
                "fhir_resource_path": self.fhir_resource_path, 
                "hl7v2_version": self.hl7v2_version,  
                "hl7v2_path": self.hl7v2_path,  
                "message_field_name": self.message_field_name, 
                "description": self.description,
                "updated": str(self.updated)}


    def save(self, commit=True, **kwargs):
        if commit:
            if not self.name:
                self.name = self.eicr_data_element
                self.code = str.upper(slugify(self.eicr_data_element))
            if not self.message_field_name:
                self.message_field_name = self.name.lower().replace(" ","_")
            super(AnonyomizedDataNeed, self).save(**kwargs)


class PatientIDType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Types: Patient ID'
        verbose_name = 'Type: Patient ID'

    def __str__(self):
        return self.code
    @property
    def as_dict(self):
        return  {"code":self.code, "name": self.name, "description": self.description}


class DataTransportType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Types: Data Transports'
        verbose_name = 'Type: Data Transport'

    def __str__(self):
        return self.code

    @property
    def as_dict(self):
        return  {"code":self.code, "name": self.name, "description": self.description}


class HealthDataType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    description = models.TextField(max_length=2048,
                                   blank=True,
                                   default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name_plural = 'Types: Health Data'
        verbose_name = 'Type: Health Data'


    @property
    def as_dict(self):
        return  {"code":self.code,
                 "name": self.name, 
                 "description": self.description,
                 "updated": str(self.updated)}
    

class ProgramAreaType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    adult_records_contain_child_records = models.BooleanField(blank=True, default=False)
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
    
    class Meta:
        verbose_name_plural = 'Types: Program Areas'
        verbose_name = 'Type: Program Area'

    def __str__(self):
        return self.name

    @property
    def as_dict(self):
        return  {"code":self.code,
                 "name": self.name, 
                 "adult_records_contain_child_records": self.adult_records_contain_child_records,
                 "description": self.description,
                 "updated": str(self.updated)}


class ReportType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    description = models.TextField(max_length=2048,
                                   blank=True,
                                   default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Types: Report'
        verbose_name = 'Type: Report'

    def __str__(self):
        return self.code
    
    @property
    def as_dict(self):
        return  {"code":self.code, "name": self.name, "description": self.description}


class Jurisdiction(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    description = models.TextField(max_length=2048, blank=True,default='')
    state = USPostalCodeField(blank=True, default='', choices=USPS_CHOICES)
    state_level = models.BooleanField(blank=True, default=False)
    origin_id = models.CharField(max_length=255, default='', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % (self.name)
    
    class Meta:
        verbose_name_plural = 'Jurisdictions'
        verbose_name = 'Jurisdiction'
        ordering = ["code"]

    @property
    def as_dict(self):
        return  {"code":self.code, "name": self.name, 
                 "state": self.state, "state_level": self.state_level,
                 "description": self.description,
                 "updated": str(self.updated)[0:16]}

    def save(self, commit=True, **kwargs):
        for s in USPS_CHOICES:
           if self.code == s[0]:
               self.state = s[0]
               self.name = s[1]
               self.state_level = True

        if commit:
            super(Jurisdiction, self).save(**kwargs)


class Partner(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.CASCADE)
    state_level = models.BooleanField(blank=True, default=False)
    state = USPostalCodeField(blank=True, default='', choices=USPS_CHOICES)
    description = models.TextField(max_length=2048,
                                   blank=True,
                                   default='')
   
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % (self.name)
    
    class Meta:
        verbose_name_plural = 'Partners'
        verbose_name = 'Partner'
        ordering = ["name"]
    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "updated": str(self.updated)}


class IntermediarySoftware(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    version = models.CharField(max_length=255, default='', blank=True)
    vendor_name = models.CharField(max_length=255, default='', blank=True)
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)
    
    class Meta:
        verbose_name_plural = 'Software: Intermediaries'
        verbose_name = 'Software:  Intermediary'
        ordering = ["code"]

    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "updated": str(self.updated)}


class IntermediarySystem(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    intermediary_software = models.ForeignKey(IntermediarySoftware, on_delete=models.CASCADE,
                                 related_name="intermediary_software", null=True,blank=True)
    source_system = models.ForeignKey('SourceSoftware', blank=True, null=True, on_delete=models.CASCADE,
                        related_name="intermediary_source_system",
                        help_text="Leave blank if original source (ie. not an intermediary system)")
    input_data_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE, 
                                blank=True, null=True, related_name="intermediary_main_data_input_type")
    input_data_other_types = models.ManyToManyField(HealthDataType, blank=True,
                                    related_name='intermediary_input_data_other_types')
    output_data_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE,
                                              blank=True, null=True, related_name="intermediary_data_output_type")
    output_data_other_types = models.ManyToManyField(HealthDataType, blank=True,
                                            related_name="intermediary_other_supported_output_data_types")
    input_transport_type = models.ForeignKey(DataTransportType, on_delete=models.CASCADE,
                                              blank=True, null=True, 
                                              related_name="intermediary_transport_in")
    input_transport_other_types = models.ManyToManyField(DataTransportType, 
                                              blank=True, related_name="intermediaryimport_transport_other_types")
    output_transport_type = models.ForeignKey(DataTransportType, on_delete=models.CASCADE,
                                              blank=True, null=True, related_name="intermediary_transport_out")
    output_transport_other_types = models.ManyToManyField(DataTransportType, blank=True,
                                            related_name="intermediaryoutput_data_other_types")
    vendor_name = models.CharField(max_length=255, default='',blank=True)
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Systems: Intermediaries'
        verbose_name = 'System: Intermediary'
        ordering = ["code"]

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)


class InergrationEngineSoftware(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    version = models.CharField(max_length=255, default='', blank=True)
    vendor_name = models.CharField(max_length=255, default='', blank=True)
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)
    
    class Meta:
        verbose_name_plural = 'Software: Inergration Engines'
        verbose_name = 'Software: Inergration Engine'
        ordering = ["code"]

    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "updated": str(self.updated)}
    

class InergrationEngineSystem(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    integration_engine_software = models.ForeignKey(InergrationEngineSoftware, on_delete=models.CASCADE,
                                 related_name="inergration_engine_software",null=True,blank=True)
    source_system = models.ForeignKey('SourceSoftware', blank=True, null=True, on_delete=models.CASCADE,
                        related_name="inergration_engine_source_system")
    input_data_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE, 
                                blank=True, null=True, related_name="inergration_engine_main_data_input_type")
    input_data_other_types = models.ManyToManyField(HealthDataType, blank=True,
                                    related_name='inergration_engine_input_data_other_types')
    output_data_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE,
                                              blank=True, null=True, related_name="inergration_engine_data_output_type")
    output_data_other_types = models.ManyToManyField(HealthDataType, blank=True,
                                            related_name="inergration_engine_other_supported_output_data_types")
    input_transport_type = models.ForeignKey(DataTransportType, on_delete=models.CASCADE,
                                              blank=True, null=True, 
                                              related_name="inergration_engine_transport_in")
    input_transport_other_types = models.ManyToManyField(DataTransportType, 
                                              blank=True, related_name="inergration_engine_import_transport_other_types")
    output_transport_type = models.ForeignKey(DataTransportType, on_delete=models.CASCADE,
                                              blank=True, null=True, related_name="inergration_engine_ransport_out")
    output_transport_other_types = models.ManyToManyField(DataTransportType, blank=True,
                                            related_name="inergration_engine_output_data_other_types")
    vendor_name = models.CharField(max_length=255, default='',blank=True)
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Systems: Inergration Engines'
        verbose_name = 'System: Inergration Engine'
        ordering = ["code"]

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)
    

class SourceSoftware(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    version = models.CharField(max_length=255, default='', blank=True)
    vendor_name = models.CharField(max_length=255, default='', blank=True)
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s)" % (self.name, self.code)
    
    class Meta:
        verbose_name_plural = 'Software: Data Sources'
        verbose_name = 'Software: Data Source'
        ordering = ["code"]
    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "updated": str(self.updated)}


class SourceSystem(models.Model):
    code = models.CharField(max_length=255, default='', unique=True)
    name = models.CharField(max_length=255, default='')
    jurisdiction = models.ForeignKey(Jurisdiction, on_delete=models.CASCADE, blank=True, null=True)
    state = USPostalCodeField(blank=True, default='', choices=USPS_CHOICES)
    software = models.ForeignKey(SourceSoftware, on_delete=models.CASCADE)
    program_areas = models.ManyToManyField(ProgramAreaType, blank=True)
    source_system = models.ForeignKey('SourceSoftware', blank=True, null=True, on_delete=models.CASCADE,
                        related_name="source_system_source_system",
                        help_text="Leave blank if original source (ie. not an intermediary system)")
    intermediary_systems = models.ManyToManyField(IntermediarySystem, blank=True,
                                    related_name="sourcesystem_intermediary_systems")
    integration_engine_systems = models.ManyToManyField(InergrationEngineSystem, blank=True,
                                    related_name="sourcesystem_integration_systems")
    input_data_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE, 
                                blank=True, null=True, related_name="source_main_data_input_type")
    input_data_other_types = models.ManyToManyField(HealthDataType, blank=True,
                                    related_name='source_input_data_other_types')
    output_data_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE,
                                              blank=True, null=True, related_name="source_data_output_type")
    output_data_other_types = models.ManyToManyField(HealthDataType, blank=True,
                                            related_name="source_other_supported_output_data_types")
    input_transport_type = models.ForeignKey(DataTransportType, on_delete=models.CASCADE,
                                              blank=True, null=True, related_name="source_transport_in")
    input_transport_other_types = models.ManyToManyField(DataTransportType, 
                                              blank=True, related_name="source_inport_transport_other_types")
    output_transport_type = models.ForeignKey(DataTransportType, on_delete=models.CASCADE,
                                              blank=True, null=True, related_name="source_transport_out")
    output_transport_other_types = models.ManyToManyField(DataTransportType, blank=True,
                                            related_name="source_output_data_other_types")
    vendor_name = models.CharField(max_length=255, default='',blank=True)
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Systems: Data Sources'
        verbose_name = 'System: Data Source'
        ordering = ["jurisdiction__code",]


    def __str__(self):
        return "%s" % (self.code)

    @property
    def integration_engine_systems_list(self):
        mylist=[]
        for i in self.integration_engine_systems.all():
            mylist.append(i.code)
        return mylist

    @property
    def intermediary_systems_list(self):
        mylist=[]
        for i in self.intermediary_systems.all():
            mylist.append(i.code)
        return mylist


    @property
    def output_data_other_types_list(self):
        mylist=[]
        for i in self.output_data_other_types.all():
            mylist.append(i.code)
        return mylist

    @property
    def output_transport_other_types_list(self):
        mylist=[]
        for i in self.output_transport_other_types.all():
            mylist.append(i.code)
        return mylist

    @property
    def program_areas_list(self):
        mylist=[]
        for i in self.program_areas.all():
            mylist.append(i.code)
        return mylist

    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name,
                 "jurisdiction":self.jurisdiction.code,
                 "program_areas":self.program_areas_list,
                 "description": self.description,
                 "updated": str(self.updated)}


class CDCOrganization(models.Model):
    code = models.CharField(max_length=255, default='',unique=True)
    name = models.CharField(max_length=255, default='')
    sub_name = models.CharField(max_length=255, default='', blank= True)
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if not self.sub_name:
            return self.name
        else:
            return "%s-%s" %(self.name, self.sub_name
                             )
    class Meta:
        verbose_name_plural = 'CDC Organizations or Programs'
        verbose_name = 'CDC Organization or Program'
        ordering = ["code"]

    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "updated": str(self.updated)}


class CDCReceivingSoftware(models.Model):
    code = models.CharField(max_length=255, default='', unique=True)
    name = models.CharField(max_length=255,default='')
    version = models.CharField(max_length=255, default='')
    vendor_name = models.CharField(max_length=255, default='')
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % (self.code)

    class Meta:
        verbose_name_plural = 'Software: CDC Recipients'
        verbose_name = 'Software: CDC Recipient'
        ordering = ["code"]

    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "version":self.version, 
                 "description": self.description,
                 "updated": str(self.updated)}


class CDCReceivingSystem(models.Model):
    code = models.CharField(max_length=255, default='',
                             unique=True)
    name = models.CharField(max_length=255, default='')
    software = models.ForeignKey(CDCReceivingSoftware, on_delete=models.CASCADE)
    intermediary_systems = models.ManyToManyField(IntermediarySystem, blank=True,
                                    related_name="cdcreceivingsystem_intermediary_systems")
    integration_engine_systems = models.ManyToManyField(InergrationEngineSystem, blank=True,
                                    related_name="cdcreceivingsystem_integration_systems")
    organization = models.ForeignKey(CDCOrganization, null=True, blank=True, on_delete=models.CASCADE)
    input_data_type = models.ForeignKey(HealthDataType, on_delete=models.CASCADE, blank=True, null=True,
                                    verbose_name="Input Data Type",)
    input_data_other_types = models.ManyToManyField(HealthDataType, blank=True,
                                            related_name="cdc_other_supported_input_types")
    input_transport_type = models.ForeignKey(DataTransportType, on_delete=models.CASCADE, 
                                    verbose_name="Input Transport Type",blank=True, null=True)
    input_transport_other_types = models.ManyToManyField(DataTransportType, blank=True,
                                            related_name="cdc_other_supported_input_types")
    vendor_name = models.CharField(max_length=255, default='', blank=True)
    vendor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor or Contractor Point of Contact")
    cdc_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="CDC Point of Contact")
    description = models.TextField(max_length=2048,blank=True,default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "%s" % (self.code)
    
    class Meta:
        verbose_name_plural = 'Systems: CDC Recipients'
        verbose_name = 'System: CDC Recipient'
        ordering = ["code"]
    
    @property
    def input_data_other_types_list(self):
        mylist=[]
        for i in self.input_data_other_types.all():
            mylist.append(i.code)
        return mylist

    @property
    def integration_engine_systems_list(self):
        mylist=[]
        for i in self.integration_engine_systems.all():
            mylist.append(i.code)
        return mylist

    @property
    def intermediary_systems_list(self):
        mylist=[]
        for i in self.intermediary_systems.all():
            mylist.append(i.code)
        return mylist

    @property
    def input_data_other_types_list(self):
        mylist=[]
        for i in self.input_data_other_types.all():
            mylist.append(i.code)
        return mylist

    @property
    def input_transport_other_types_list(self):
        mylist=[]
        for i in self.input_transport_other_types.all():
            mylist.append(i.code)
        return mylist

    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name,
                 "input_data_type": self.input_data_type,
                 "input_data_other_types": self.input_data_other_types_list,
                 "input_transport_type": self.input_transport_type, 
                 "input_transport_other_types": str(self.input_transport_other_types_list),
                 "description": self.description,
                 "updated": str(self.updated)}


class Connection(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, null=True)
    program_area = models.ForeignKey(ProgramAreaType, on_delete=models.CASCADE, null=True)
    source_system = models.ForeignKey(SourceSystem, on_delete=models.CASCADE, null=True)
    intermediary_systems = models.ManyToManyField(IntermediarySystem, blank=True,
                                    related_name="connection_intermediary_systems")
    integration_engine_systems = models.ManyToManyField(InergrationEngineSystem, blank=True,
                                    related_name="connection_intermediary_systems")
    cdc_receiving_system = models.ForeignKey(CDCReceivingSystem, on_delete=models.CASCADE, null=True)
    description = models.TextField(max_length=2048,blank=True,default='')
    vendor_or_contractor_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="Vendor or Contractor Point of Contact")
    cdc_poc = models.TextField(max_length=2048, blank=True, default='', 
                                  verbose_name="CDC Point of Contact")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s-->%s" % (self.source_system,
                            self.cdc_receiving_system)

    class Meta:
        verbose_name_plural = 'Connections'
        verbose_name = 'Connection'
        unique_together = (('partner','source_system','cdc_receiving_system'),)
        ordering = ["partner"]

    @property
    def integration_engine_systems_list(self):
        mylist=[]
        for i in self.integration_engine_systems.all():
            mylist.append(i.code)
        return mylist

    @property
    def intermediary_systems_list(self):
        mylist=[]
        for i in self.intermediary_systems.all():
            mylist.append(i.code)
        return mylist

    @property
    def source_main_output_data_type(self):
        return self.source_system.output_data_type

    @property
    def transport_data_type(self):
        return self.source_system.output_transport_type


    @property
    def cdc_receiving_main_input_data_type(self):
        return self.cdc_receiving_system.input_data_type

    @property
    def as_dict(self):
        return  {"partner": self.partner.code,
                 "jurisdiction": self.partner.jurisdiction.code,
                 "partner_name": self.partner.name,
                 "state_partner": self.partner.state_level,
                 "source_system_code": self.source_system.code,
                 "source_system_name": self.source_system.name,
                 "source_system_output_data_type": self.source_system.output_data_type ,
                 "source_system_output_transport_type": self.source_system.output_transport_type,
                 "source_system_output_transport_other_types": self.source_system.output_transport_other_types_list,
                 "cdc_receiving_system_code": self.cdc_receiving_system.code,
                 "cdc_receiving_system_name": self.cdc_receiving_system.name,
                 "cdc_receiving_system_input_data_type": self.cdc_receiving_system.input_data_type,
                 "cdc_receiving_other_input_data_types": self.cdc_receiving_system.input_data_other_types_list,
                 "description": self.description,
                 "updated": str(self.updated)}


class RMetaMessage(models.Model):
    message_id = models.CharField(max_length=36, default=uuid.uuid4,
                             unique=True, db_index=True)
    initial_message_id = models.CharField(max_length=36, default='', blank=True,
                             db_index=True,
                             help_text="Link to the initial message_id for a given case/person.")
    encompassing_encounter_id = models.CharField(max_length=64, default='', blank=True,
                             db_index=True,
                             help_text="Link to the initial message_id for a given case/person.")
    source_system_case_report_type = models.ForeignKey(ReportType, on_delete=models.CASCADE)
    source_system = models.ForeignKey(SourceSystem, on_delete=models.CASCADE)
    cdc_receiving_system = models.ForeignKey(CDCReceivingSystem, on_delete=models.CASCADE)
    report_url = models.URLField(max_length=512, blank=True, default='')
    reportable_condition_flag = models.BooleanField(default=False, null=True)
    notifiable_condition_flag = models.BooleanField(default=False, null=True)
    current_case_status = models.CharField(max_length=15, default='', blank=True, 
                                           db_index=True, choices=CASE_STATUS_CHOICES)
    final_case_status = models.CharField(max_length=15, default='', blank=True, 
                                         db_index=True, choices=CASE_STATUS_CHOICES)
    final_case_status_date = models.DateField(blank=True, null=True)
    source_system_node = models.CharField(max_length=36, blank=True)
    source_system_transaction_id = models.CharField(max_length=36, blank=True, default='')
    source_system_initial_case_report_id = models.CharField(max_length=36, blank=True, default='')
    source_system_case_report_link_id = models.CharField(max_length=36, blank=True, default='')
    source_systems_patient_id_issuer = models.CharField(max_length=36, blank=True, default='')
    source_fhir_bundle_payload_url = models.URLField(max_length=512, blank=True, null=True)
    source_data_payload_pointer = models.CharField(max_length=200, blank=True, default='')
    source_patient_id_type = models.ForeignKey(PatientIDType, on_delete=models.CASCADE, null=True, blank=True)
    source_patient_id_issuer = models.CharField(max_length=200, blank=True, default='',
                                help_text="Assigning Authority/Issuer") 
    source_data_format = models.ForeignKey(HealthDataType, null=True, blank=True, on_delete=models.CASCADE)
    source_data_transport_type = models.ForeignKey(DataTransportType, null=True, blank=True, on_delete=models.CASCADE)
    
    # Core test data...just the highlights please
    test_ordered_test_loinc_code = models.CharField(max_length=36, blank=True, default='')
    test_ordered_test_device_identifier = models.CharField(max_length=36, blank=True, default='')
    test_ordered_result_loinc_code= models.CharField(max_length=36, blank=True, default='')
    test_ordered_snomed_code = models.CharField(max_length=36, blank=True, default='')
    test_ordered_result_date = models.DateField(blank=True, null=True)
    test_ordered_accession_num_or_specimen_id = models.CharField(max_length=36, blank=True, default='')
    # CDC Recip 
    cdc_receiving_system_status = models.CharField(max_length=36, blank=True, default='')
    cdc_receiving_system_url = models.URLField(max_length=512, blank=True, null=True)
    cdc_receiving_case_report_id = models.CharField(max_length=36, blank=True, default='')
    # Patient Data
    patient_age = models.PositiveSmallIntegerField(blank=True, default=0)
    patient_race = models.CharField(max_length=36, blank=True, default='')
    patient_ethnicity = models.CharField(max_length=36, blank=True, default='')
    patient_sex = models.CharField(max_length=36, blank=True, default='')
    patient_residence_zip_code= models.CharField(max_length=36, blank=True, default='')
    patient_residence_county = models.CharField(max_length=128, blank=True, default='')
    patient_date_of_birth = models.DateField(blank=True, null=True)
    patient_address_state = USPostalCodeField(blank=True, default='', choices=USPS_CHOICES)
    patient_address_zip_code= USZipCodeField(blank=True, default='')
    patient_address_country_code = models.CharField(max_length=2, blank=True, default='US')
    patient_phone_number = models.CharField(max_length=15, blank=True, default='')
    patient_mobile_phone_number = models.CharField(max_length=15, blank=True, default='')
    patient_email = models.EmailField(max_length=255, blank=True, default='')
    patient_insurance_member_id = models.CharField(max_length=128, blank=True, default='')
    patient_insurance_plan_id = models.CharField(max_length=128, blank=True, default='')
    patient_seen_identifier = models.CharField(max_length=128, blank=True, default='')
    patient_seen_identifier_issuer = models.CharField(max_length=128, blank=True, default='')
    # Hashes
    patient_dob_and_mobilephone_hash = models.CharField(max_length=64, blank=True, default='')
    patient_email_and_mobilephone_hash = models.CharField(max_length=64, blank=True, default='')
    patient_dob_email_hash = models.CharField(max_length=64, blank=True, default='')
    mrn_and_node_hash = models.CharField(max_length=64, blank=True, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    cdc_payload_json = models.TextField(blank=True, default='{}')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, commit=True, **kwargs):
        if commit:
            super(RMetaMessage, self).save(**kwargs)


    def __str__(self):
        return "%s" % (self.message_id)

    class Meta:
        verbose_name_plural = 'API Messages'
        verbose_name = 'API Message'


    @property
    def dob_mobile_hash(self):
        if not self.patient_dob_and_mobilephone_hash:
            return ""
        return "%s..." % (self.patient_dob_and_mobilephone_hash[0:5])

    @property
    def is_initial_message(self):
        if self.initial_message_id:
            return False
        return True
    
    @property
    def as_dict(self):
        return  {"message_id":self.message_id,
                 "inital_message_id": self.initial_message_id,
                 "is_inital_message": self.is_initial_message,
                 "encompassing_encounter_id": self.encompassing_encounter_id,
                 "message_type": self.source_system_case_report_type.code,
                 "source_system_code": self.source_system.code,
                 "patient_dob_and_mobilephone_hash": self.patient_dob_and_mobilephone_hash,
                 "patient_email_and_mobilephone_hash": self.patient_email_and_mobilephone_hash,
                 "patient_dob_email_hash": self.patient_dob_email_hash,
                 "mrn_and_node_hash": self.mrn_and_node_hash,
                 "description": self.description,
                 "updated": str(self.updated)}