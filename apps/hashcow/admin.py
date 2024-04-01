from django.contrib import admin
from .models import HashedMessage

class HashedMessageAdmin(admin.ModelAdmin):
    list_display = ('hashlink',
                    'patient_age',
                    'patient_sex',
                    'initial_message_id',
                    'encompassing_encounter_id',
                    'source_system_case_report_type',
                    'cdc_receiving_system',
                    'dob_mobile',
                    'dob_email',
                    'email_mobile',
                    'mrn_node',
                    'ins_plan_member',
                    'created')

    search_fields = ('hashlink', 'initial_message_id', 
                     'source_system', 
                     'encompassing_encounter_id',
                     'cdc_receiving_system')

admin.site.register(HashedMessage, HashedMessageAdmin)
