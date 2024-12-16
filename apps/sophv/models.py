
from django.db import models

class DataElement(models.Model):
    oid = models.CharField(max_length=64, db_index=True)
    common_name = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    data_element_identifier_csv = models.CharField(max_length=200)
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

