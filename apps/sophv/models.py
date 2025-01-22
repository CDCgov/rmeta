from django.db import models

PRIORITY_CHOICES = (('R','R'),('1','1'),('2','2'))

class MDN(models.Model):
    data_element_name= models.CharField(max_length=200, blank=True)
    data_element_identifier_csv= models.CharField(max_length=200, blank=True)
    common_name = models.CharField(max_length=200, blank=True)
    oid	= models.CharField(max_length=100, blank=True)
    data_element_description = models.CharField(max_length=200, blank=True)
    data_element_type = models.CharField(max_length=200, blank=True)
    cdc_priority = models.CharField(max_length=1, blank=True, choices=PRIORITY_CHOICES)
    may_repeat = models.CharField(max_length=64, blank=True)
    value_set_name = models.CharField(max_length=200, blank=True)
    phinvads_hyperlink = models.CharField(max_length=200, blank=True)
    phinvads_fhir_hyperlink  = models.CharField(max_length=200, blank=True)
    static_csv_hyperlink= models.CharField(max_length=200, blank=True)
    value_set_code = models.CharField(max_length=200, blank=True)
    repeating_group_element = models.CharField(max_length=200, blank=True)
    repeating_group_name = models.CharField(max_length=200, blank=True)
    csv_implementation_notes = models.TextField(blank=True)
    sample_value = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)


    class Meta:
        verbose_name="MDN Data Element"
        verbose_name_plural="MDN Data Elements"

    def __str__(self):
        return f"{self.data_element_name}"
    
    def to_dict(self):
        return {
            "data_element_name": self.data_element_name,
            "data_element_identifier_csv": self.data_element_identifier_csv,
            "common_name": self.common_name,
            "oid": self.oid,
            "data_element_description": self.data_element_description,
            "data_element_type": self.data_element_type,
            "cdc_priority": self.cdc_priority,
            "may_repeat": self.may_repeat,
            "value_set_name": self.value_set_name,
            "phinvads_hyperlink": self.phinvads_hyperlink,
            "phinvads_fhir_hyperlink": self.phinvads_fhir_hyperlink,
            "static_csv_hyperlink": self.static_csv_hyperlink,
            "value_set_code": self.value_set_code,
            "repeating_group_element": self.repeating_group_element,
            "repeating_group_name": self.repeating_group_name,
            "csv_implementation_notes": self.csv_implementation_notes,
            "sample_value": self.sample_value,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
        }


class DataElement(models.Model):
    oid = models.CharField(max_length=64, db_index=True)
    common_name = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    data_element_identifier_csv = models.CharField(max_length=200, blank=True)
    version = models.CharField(max_length=10, blank=True)
    code = models.CharField(max_length=64, blank=True, db_index=True)
    code_display = models.CharField(max_length=200, blank=True)
    code_system = models.CharField(max_length=200, blank=True)
    code_system_name = models.CharField(max_length=200, blank=True)
    code_system_version = models.CharField(max_length=200, blank=True)
    fhir_code = models.CharField(max_length=64, blank=True, db_index=True)
    fhir_code_display = models.CharField(max_length=200, blank=True)
    fhir_code_system = models.CharField(max_length=200, blank=True)
    fhir_code_system_name = models.CharField(max_length=200, blank=True)
    fhir_code_system_version = models.CharField(max_length=200, blank=True)    
    description = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
  
    def __str__(self):
        return f"{self.common_name}:{self.code}"
    
    @property
    def to_dict(self):
            return {
                "oid": self.oid,
                "common_name": self.common_name,
                "name": self.name,
                "data_element_identifier_csv": self.data_element_identifier_csv,
                "version": self.version,
                "code": self.code,
                "code_display": self.code_display,
                "code_system": self.code_system,
                "code_system_name": self.code_system_name,
                "code_system_version": self.code_system_version,
                "fhir_code": self.fhir_code,
                "fhir_code_display": self.fhir_code_display,
                "fhir_code_system": self.fhir_code_system,
                "fhir_code_system_name": self.fhir_code_system_name,
                "fhir_code_system_version": self.fhir_code_system_version,
                "description": self.description,
                "date_created": self.date_created,
                "date_updated": self.date_updated,
            }

class OID(models.Model):
    oid = models.CharField(max_length=64, db_index=True)
    common_name = models.CharField(max_length=100, db_index=True)
    title = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=200, blank=True)
    data_element_identifier_csv = models.CharField(max_length=200, blank=True)
    version = models.CharField(max_length=10, blank=True)
    code = models.CharField(max_length=64, blank=True, db_index=True)
    code_display = models.CharField(max_length=200, blank=True)
    code_system = models.CharField(max_length=200, blank=True)
    code_system_name = models.CharField(max_length=200, blank=True)
    code_system_version = models.CharField(max_length=200, blank=True)
    fhir_code = models.CharField(max_length=64, blank=True, db_index=True)
    fhir_code_display = models.CharField(max_length=200, blank=True)
    fhir_code_system = models.CharField(max_length=200, blank=True)
    fhir_code_system_name = models.CharField(max_length=200, blank=True)
    fhir_code_system_version = models.CharField(max_length=200, blank=True)    
    description = models.TextField(blank=True)
    date_created = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    class Meta:
        verbose_name="OID + Code Value"
        verbose_name_plural="OID + Code Values"
    def __str__(self):
        return f"{self.oid}:{self.code}"
    
    @property
    def to_dict(self):
            return {
                
                "pk": self.oid+":"+self.code,
                "oid": self.oid+":"+self.code,
                "common_name": self.common_name,
                "name": self.name,
                "title": self.title,
                "data_element_identifier_csv": self.data_element_identifier_csv,
                "version": self.version,
                "code": self.code,
                "code_display": self.code_display,
                "code_system": self.code_system,
                "code_system_name": self.code_system_name,
                "code_system_version": self.code_system_version,
                "fhir_code": self.fhir_code,
                "fhir_code_display": self.fhir_code_display,
                "fhir_code_system": self.fhir_code_system,
                "fhir_code_system_name": self.fhir_code_system_name,
                "fhir_code_system_version": self.fhir_code_system_version,
                "description": self.description,
                "date_created": self.date_created,
                "date_updated": self.date_updated,
            }