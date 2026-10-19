from django.contrib import admin
from django.db.models import Count
from .models import (DataElementType, DomainType, DataClassType, 
                     UseCaseType, CDCDataElements, DataElement,
                     HL7Segment, HL7Message, MessageMappingGuide,
                     CodeReference, Uses)

class MessageMappingGuideAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'csv_guide_url', 'hl7v2_guide_url')
    search_fields = ('code', 'name')

admin.site.register(MessageMappingGuide, MessageMappingGuideAdmin)

class HL7SegmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'example')
    search_fields = ('code', 'name')

admin.site.register(HL7Segment, HL7SegmentAdmin)

class HL7MessageAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'get_segments', 'pub_health_germain', 'example')
    search_fields = ('code', 'name')

admin.site.register(HL7Message, HL7MessageAdmin)

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


@admin.register(Uses)
class UsesAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'code_reference_count')
    search_fields = ('name', 'url')
    ordering = ('name', 'url')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _code_reference_count=Count('code_references', distinct=True)
        )

    @admin.display(description='Code references', ordering='_code_reference_count')
    def code_reference_count(self, obj):
        return obj._code_reference_count


@admin.register(CodeReference)
class CodeReferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'oid', 'version', 'status', 'use_count')
    list_filter = ('status', 'version')
    search_fields = ('name', 'title', 'url', 'oid', 'description',
                     'uses__name', 'uses__url')
    ordering = ('name', 'url')
    autocomplete_fields = ('uses',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _use_count=Count('uses', distinct=True)
        )

    @admin.display(description='Uses', ordering='_use_count')
    def use_count(self, obj):
        return obj._use_count
