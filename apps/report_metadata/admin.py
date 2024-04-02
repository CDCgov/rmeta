from django.contrib import admin
from .models import (HealthDataType, DataTransportType, PatientIDType, 
                     ReportType, Jurisdiction, Partner, SourceSoftware,
                     SourceSystem,CDCOrganization, CDCReceivingSoftware,
                     CDCReceivingSystem, Connection, RMetaMessage,
                     AnonyomizedDataNeed,  ProgramAreaType,IntermediarySoftware,
                     IntermediarySystem, PersonHashType, InergrationEngineSoftware, 
                     InergrationEngineSystem)



class PersonHashTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'prefix','series', 'salt', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(PersonHashType, PersonHashTypeAdmin)

class AnonyomizedDataNeedAdmin(admin.ModelAdmin):
    list_display = ('name','code',  'keep', 'in_syndromic_message', 'hipaa_id', 'pprl_hash', 
                    'eicr_template','description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(AnonyomizedDataNeed, AnonyomizedDataNeedAdmin)

class HealthDataTypeAdmin(admin.ModelAdmin):
    list_display = ('name','code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(HealthDataType, HealthDataTypeAdmin)


class ProgramAreaTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(ProgramAreaType, ProgramAreaTypeAdmin)


class DataTransportTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(DataTransportType, DataTransportTypeAdmin)


class PatientIDTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(PatientIDType, PatientIDTypeAdmin)


class ReportTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(ReportType, ReportTypeAdmin)


class JurisdictionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'state',  'state_level', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(Jurisdiction, JurisdictionAdmin)


class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'jurisdiction','state_level', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(Partner, PartnerAdmin)


class SourceSoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(SourceSoftware, SourceSoftwareAdmin)

class SourceSystemAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'jurisdiction', 'program_areas_list', 'output_data_type',
                    'description','updated')
    search_fields = ('code','jurisdiction__code','program_areas__code','description')
admin.site.register(SourceSystem, SourceSystemAdmin)


class IntermediarySoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(IntermediarySoftware, IntermediarySoftwareAdmin)


class IntermediarySystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'output_data_type',
                    'description','updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(IntermediarySystem, IntermediarySystemAdmin)


class  InergrationEngineSoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(InergrationEngineSoftware, InergrationEngineSoftwareAdmin)


class InergrationEngineSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'output_data_type',
                    'description','updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(InergrationEngineSystem, InergrationEngineSystemAdmin)


class CDCOrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description','updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(CDCOrganization, CDCOrganizationAdmin)


class CDCReceivingSoftwareAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'version', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(CDCReceivingSoftware, CDCReceivingSoftwareAdmin)


class CDCReceivingSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 
                    'intermediary_systems_list',
                    'integration_engine_systems_list',
                    'input_data_type', 
                    'input_transport_type', 'description', 'updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(CDCReceivingSystem, CDCReceivingSystemAdmin)


class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('partner', 'source_system', 
                    'cdc_receiving_system', 
                    'intermediary_systems_list',
                    'integration_engine_systems_list',
                    'description', 'updated')
    search_fields = ('partner.code','partner.jurisdiction.code','description',)
admin.site.register(Connection, ConnectionAdmin)


class RMetaMessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'initial_message_id', 
                    'encompassing_encounter_id',
                    'source_system_case_report_type',
                    'source_system', 
                    'cdc_receiving_system',
                    'dob_mobile_hash',
                    'updated')

    search_fields = ('message_id', 'initial_message_id', 
                     'source_system__code', 'cdc_receiving_system__code')
admin.site.register(RMetaMessage, RMetaMessageAdmin)
