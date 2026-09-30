from django.contrib import admin
from .models import DataElementType, DomainType, DataClassType, UseCaseType, CDCDataElements, DataElement


class DataElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'data_class', 'uscdi_url',
                    'hl7v2_segment_type', 'hl7v2_data_type', 'hl7v2_field_position',
                    'hl7v2_component_position', 'hl7v2_usage', 'hl7v2_cardinality')
    search_fields = ('name', 'description')

admin.site.register(DataElement, DataElementAdmin)

# create a model admin for CDCDataElements
class CDCDataElementsAdmin(admin.ModelAdmin):
    list_display = ('UseCase', 'Requester', 'DataElementName', 'Description', 'In_USCDI', 'If_Data_Element_Is_In_USCDI_What_Level_Is_It', 'Remarks')
    search_fields = ('UseCase', 'Requester', 'DataElementName', 'Description', 'In_USCDI', 'If_Data_Element_Is_In_USCDI_What_Level_Is_It', 'Remarks')

admin.site.register(CDCDataElements, CDCDataElementsAdmin)


class DataElementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 
                    'data_class', 'use_case', 'description',
                    'fhir_location', 'fhir_example_value_1', 'fhir_example_value_2',
                    'hl7v2_location', 'hl7v2_example_value_1', 'hl7v2_example_value_2',
                    'uscdi_url',
                    'associated_ig_or_profile_urls' ,
                    'associated_us_core_profile_urls' 
                    )
    search_fields = ('code', 'name', 'use_case__name', 'uscdi_uuid')


admin.site.register(DataElementType, DataElementTypeAdmin)


class DomainTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'updated')
    search_fields = ('code', 'name', 'uscdi_uuid')

admin.site.register(DomainType, DomainTypeAdmin)


class DataClassTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'updated')
    search_fields = ('code', 'name', 'uscdi_uuid')

admin.site.register(DataClassType, DataClassTypeAdmin)


class UseCaseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated')
    search_fields = ('code', 'name', 'uscdi_uuid')

admin.site.register(UseCaseType, UseCaseTypeAdmin)
