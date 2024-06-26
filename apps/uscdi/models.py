from django.db import models

from django.db import models
import uuid
from slugify import slugify
from django.conf import settings

CASE_STATUS_CHOICES = (('SUSPECTED','SUSPECTED'),('PROBABLE','PROBABLE'),
                       ('CONFIRMED','CONFIRMED'))


class DomainType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True, blank=True)
    name = models.CharField(max_length=255, default='')
    uscdi_uuid =  models.UUIDField(blank=True, null=True)
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Types: Domains'
        verbose_name = 'Type: Domain'

    def __str__(self):
        return self.name
    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "uscdi_uuid":self.uscdi_uuid}

    def save(self, commit=True, **kwargs):
        if commit:
            if not self.code:
                self.code = str.upper(slugify(self.name.upper()))
            super(DomainType, self).save(**kwargs)

class DataClassType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True, blank=True)
    name = models.CharField(max_length=255, default='')
    uscdi_uuid =  models.UUIDField(blank=True, null=True)
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Types: Data Classes'
        verbose_name = 'Type: Data Class'

    def __str__(self):
        return self.name
    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "uscdi_uuid":self.uscdi_uuid}

    def save(self, commit=True, **kwargs):
        if commit:
            if not self.code:
                self.code = str.upper(slugify(self.name.upper()))
            super(DataClassType, self).save(**kwargs)

class UseCaseType(models.Model):

    code = models.CharField(max_length=255, default='',unique=True, blank=True)
    name = models.CharField(max_length=255, default='')
    uscdi_uuid =  models.UUIDField(blank=True, null=True)
    description = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Types: Use Cases'
        verbose_name = 'Type: Use Case'

    def __str__(self):
        return self.name
    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                 "uscdi_uuid":self.uscdi_uuid}

    def save(self, commit=True, **kwargs):
        if commit:
            if not self.code:
                self.code = str.upper(slugify(self.name.upper()))
            super(UseCaseType, self).save(**kwargs)


class DataElementType(models.Model):
    code = models.CharField(max_length=255, default='',unique=True, blank=True)
    name = models.CharField(max_length=255, default='')
    description = models.TextField(max_length=2048, blank=True, default='')
    uscdi_uuid =  models.UUIDField(blank=True, null=True)
    domain = models.ForeignKey(DomainType, on_delete=models.CASCADE)
    data_class = models.ForeignKey(DataClassType, on_delete=models.CASCADE)
    use_case = models.ForeignKey(UseCaseType, on_delete=models.CASCADE)
    submission_status = models.CharField(max_length=20, default='', blank=True)
    additional_information = models.TextField(default='', blank=True)
    in_uscdi = models.BooleanField(default=False, blank=True)
    current_uscdi_level = models.CharField(max_length=20, default='', blank=True)
    uscdi_url = models.URLField(default='', blank=True)
    applicable_vocabulary_standards = models.CharField(max_length=512, default='', blank=True)
    associated_project = models.CharField(max_length=128, default='', blank=True)  
    associated_project_urls = models.CharField(max_length=512, default='', blank=True)
    associated_reporting_program = models.CharField(max_length=128, default='', blank=True)
    associated_ig_or_profile = models.CharField(max_length=128, default='', blank=True)
    associated_ig_or_profile_urls = models.CharField(max_length=512, default='', blank=True)
    associated_us_core_profile = models.CharField(max_length=128, default='', blank=True)
    associated_us_core_profile_urls = models.CharField(max_length=512, default='', blank=True)
    cda_xpath = models.TextField(max_length=2048, blank=True, default='')
    fhir_path = models.TextField(max_length=2048, blank=True, default='')
    hl7v2_path = models.TextField(max_length=2048, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Types: Data Elements'
        verbose_name = 'Type: Data Element'

    def __str__(self):
        return self.name
    @property
    def as_dict(self):
        return  {"code":self.code, 
                 "name": self.name, 
                 "description": self.description,
                "domain":str(self.domain),
                "data_class":str(self.data_class),
                "use_case":str(self.use_case),           
                "uscdi_uuid": self.uscdi_uuid,
                "submission_status":self.submission_status,
                "additional_information":self.additional_information,
                "in_uscdi":self.in_uscdi,
                "current_uscdi_level":self.current_uscdi_level,
                "uscdi_url":self.uscdi_url,
                "applicable_vocabulary_standards":self.applicable_vocabulary_standards,
                "associated_project":self.associated_project,
                "associated_project_urls":self.associated_project_urls,
                "associated_reporting_program":self.associated_reporting_program,
                "associated_ig_or_profile":self.associated_ig_or_profile,
                "associated_ig_or_profile_urls":self.associated_ig_or_profile_urls,
                "associated_us_core_profile":self.associated_us_core_profile,
                "associated_us_core_profile_urls":self.associated_us_core_profile_urls,
                "updated": str(self.updated) }

    def save(self, commit=True, **kwargs):
        if commit:
            if not self.code:
                self.code = "%s-%s-%s-%s" % (str.upper(slugify(self.name.upper())),
                                             self.data_class.code,
                                             self.domain.code,
                                             self.use_case.code)
            super(DataElementType, self).save(**kwargs)


class CDCDataElements(models.Model):
    UseCase = models.ForeignKey(UseCaseType, on_delete=models.CASCADE)
    Requester = models.CharField(max_length=255)
    DataElementName = models.CharField(max_length=255)
    Description = models.TextField()
    In_USCDI = models.CharField(max_length=255)
    If_Data_Element_Is_In_USCDI_What_Level_Is_It = models.CharField(max_length=255)
    Remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.DataElementName


    class Meta:
        verbose_name_plural = 'USCDI+ CDC Recommended Data Elements'
        verbose_name = 'USCDI+ CDC Recommended Data Element'
