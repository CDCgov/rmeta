from django.contrib import admin
from .models import DataElement, OID, MDN

class MDNAdmin(admin.ModelAdmin):
    list_display = ('data_element_name', 'oid', 'data_element_identifier_csv', 'data_element_type', 'cdc_priority', 'static_csv_hyperlink')
    search_fields = ('data_element_name', 'oid', 'data_element_identifier_csv', 'data_element_type', 'cdc_priority', 'static_csv_hyperlink')
    list_filter = ('data_element_name', 'oid', 'data_element_identifier_csv', 'data_element_type', 'cdc_priority')


admin.site.register(MDN, MDNAdmin)

class DataElementAdmin(admin.ModelAdmin):
    list_display = ('code', 'common_name', 'code_display', 'code_system', 'name', 'code_system_version')
    search_fields = ('common_name', 'name', 'code', 'code_display', 'code_system', 'code_system_version')
    list_filter = ('common_name', 'code', 'code_display', 'code_system', 'code_system_version')
    ordering = ('common_name', 'code', 'code_display', 'code_system', 'code_system_version')

admin.site.register(DataElement, DataElementAdmin)

class OIDAdmin(admin.ModelAdmin):
    list_display = ('code_display', 'code', 'oid', 'name','title', 'fhir_code','code_system')
    search_fields = ('oid', 'common_name', 'name', 'code', 'code_system', )

admin.site.register(OID, OIDAdmin)