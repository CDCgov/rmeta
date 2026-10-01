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

class DataElement(models.Model):
    """One canonical USCDI data element with a representative MMG mapping."""

    # Add model field names to this list to omit their column from both the
    # CSV and JSON downloads. These names are also the exported column headers.
    EXPORT_EXCLUDED_COLUMNS = [
        "id",
        "uscdi_uuid",
    ]

    name = models.CharField(max_length=255, default='')
    code = models.CharField(max_length=255, default='',unique=True, blank=True)
    uscdi_url = models.URLField(default='', blank=True)
    description = models.TextField(max_length=2048, blank=True, default='')
    uscdi_uuid =  models.UUIDField(blank=True, null=True)
    domain = models.ForeignKey(DomainType, on_delete=models.CASCADE)
    data_class = models.ForeignKey(DataClassType, on_delete=models.CASCADE)
    data_class_description = models.TextField(max_length=2048, blank=True, default='')
    use_case = models.ForeignKey(UseCaseType, on_delete=models.CASCADE)
    additional_information = models.TextField(default='', blank=True)
    in_uscdi = models.BooleanField(default=False, blank=True)

    applicable_vocabulary_standards = models.CharField(max_length=512, default='', blank=True)
    classification_level = models.CharField(max_length=255, default='', blank=True)
    data_element = models.CharField(max_length=255, default='', blank=True)
    data_element_description = models.TextField(max_length=2048, blank=True, default='')
    applicable_standards = models.TextField(max_length=2048, blank=True, default='')
    fhir_associated_ig_or_profile_urls = models.CharField(max_length=512, default='', blank=True)
    fhir_associated_us_core_profile_urls = models.CharField(max_length=512, default='', blank=True)    
    fhir_path = models.CharField(max_length=256, blank=True, default='', help_text="e.g., Patient.birthDate")


    # HL7v2 mapping Fields
    hl7v2_legacy_identifier = models.CharField(max_length=255, default='', blank=True)
    hl7v2_identifier = models.CharField(max_length=255, default='', blank=True) 
    hl7v2_message_context = models.CharField(max_length=255, default='', blank=True)
    hl7v2_data_type = models.CharField(max_length=255, default='', blank=True)
    hl7v2_segment_type = models.CharField(max_length=255, default='', blank=True)
    hl7v2_field_position = models.IntegerField(default=0, blank=True)
    hl7v2_component_position = models.IntegerField(default=0, blank=True)
    hl7v2_usage = models.CharField(max_length=255, default='', blank=True)
    hl7v2_cardinality = models.CharField(max_length=255, default='', blank=True)
    hl7v2_literalFieldValues = models.TextField(max_length=2048, blank=True, default='')
    hl7v2_repeatingGroupElementType = models.CharField(max_length=255, default='', blank=True)
    hl7v2_sampleSegment = models.TextField(max_length=2048, blank=True, default='')


    # Message Mapping Guides
    mm_elementId = models.CharField(max_length=256, blank=True, default='')
    mm_containingGuideId = models.CharField(max_length=256, blank=True, default='')
    mm_containingGuideName = models.CharField(max_length=256, blank=True, default='')
    mm_containingGuideStatus = models.CharField(max_length=64, blank=True, default='')
    mm_containingBlockId = models.CharField(max_length=256, blank=True, default='')
    mm_matchMethod = models.CharField(max_length=32, blank=True, default='')
    mm_matchScore = models.FloatField(blank=True, null=True)
    mm_guideId = models.CharField(max_length=256, blank=True, default='')
    mm_guideInternalVersion = models.CharField(max_length=256, blank=True, default='')
    mm_blockId = models.CharField(max_length=256, blank=True, default='')
    mm_ordinal = models.IntegerField(default=0, blank=True)
    mm_name = models.CharField(max_length=256, blank=True, default='')
    mm_description = models.TextField(blank=True, default='')
    mm_shortName = models.CharField(max_length=256, blank=True, default='')
    mm_comments = models.TextField(blank=True, default='')
    mm_status = models.CharField(max_length=256, blank=True, default='')
    mm_dataType = models.CharField(max_length=256, blank=True, default='')
    mm_businessRules = models.TextField(blank=True, default='')
    mm_isUnitOfMeasure = models.BooleanField(default=False, blank=True)
    mm_codeSystem = models.CharField(max_length=256, blank=True, default='')
    mm_legacyPriority = models.CharField(max_length=256, blank=True, default='')
    mm_priority = models.CharField(max_length=256, blank=True, default='')
    mm_isRepeat = models.BooleanField(default=False, blank=True)
    # MMGAT uses values such as "N", "Y", "Y/2", and "Y/3".  Keeping the
    # source value preserves the repetition bound that a BooleanField loses.
    mm_mayRepeat = models.CharField(max_length=16, blank=True, default='')
    mm_valueSetCode = models.CharField(max_length=256, blank=True, default='')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @classmethod
    def export_field_names(cls):
        """Return the stable model-field order used by CSV and JSON exports."""

        excluded_columns = set(cls.EXPORT_EXCLUDED_COLUMNS)
        return tuple(
            field.name
            for field in cls._meta.concrete_fields
            if field.name not in excluded_columns
        )

    @property
    def as_json(self):
        """Return all concrete fields as a JSON-compatible ordered dictionary."""

        result = {}
        export_fields = set(self.export_field_names())
        for field in self._meta.concrete_fields:
            if field.name not in export_fields:
                continue
            value = getattr(self, field.name)
            if field.is_relation:
                value = str(value) if value is not None else None
            elif value is not None and hasattr(value, "isoformat"):
                value = value.isoformat()
            elif value is not None and field.get_internal_type() == "UUIDField":
                value = str(value)
            result[field.name] = value
        return result

    @property
    def as_dict(self):
        """Backward-compatible alias for the complete export representation."""

        return self.as_json

    def save(self, commit=True, **kwargs):
        if commit:
            if not self.code:
                self.code = "%s-%s-%s-%s" % (str.upper(slugify(self.name.upper())),
                                             self.data_class.code,
                                             self.domain.code,
                                             self.use_case.code)
            super(DataElement, self).save(**kwargs)

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


    fhir_location = models.CharField(max_length=256, default='', blank=True)
    fhir_example_value_1 = models.CharField(max_length=128, default='', blank=True)
    fhir_example_value_2 = models.CharField(max_length=128, default='', blank=True)
    fhir_more_details = models.TextField(max_length=2048, blank=True, default='')

    hl7v2_location = models.CharField(max_length=32, default='', blank=True)
    hl7v2_example_value_1 = models.CharField(max_length=128, default='', blank=True)
    hl7v2_example_value_2 = models.CharField(max_length=128, default='', blank=True)
    hl7v2_more_details = models.TextField(max_length=2048, blank=True, default='')
    
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
