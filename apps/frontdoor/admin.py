from django.contrib import admin
from .models import (Submission, SubmissionReceipt, Submitter, 
                     Origin, Facility, Destination, TransactionType)

class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'postal_code')
    search_fields = ('code', 'name', 'description')
admin.site.register(Facility, FacilityAdmin)

class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description', 'url', 'date_updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(Destination, DestinationAdmin)

class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('code', 'name', 'description')

admin.site.register(TransactionType, TransactionTypeAdmin)

class OriginAdmin(admin.ModelAdmin):
    list_display = ('name', 'ori','description', 'postal_code', 'facility', 'date_updated')
    search_fields = ('code', 'name', 'description')
admin.site.register(Origin, OriginAdmin)

class SubmitterAdmin(admin.ModelAdmin):
    list_display = ('name', 'submitter_code','description', 'application', 'url', 'date_updated')
    search_fields = ('code', 'name', 'description')

admin.site.register(Submitter, SubmitterAdmin)

class SubmissionReceiptAdmin(admin.ModelAdmin):
    list_display = ('submitter_code',
                    'status')
    search_fields = ('submitter__origin__code', 'submitter__tcn', 'submitter__tcr', 'status')

admin.site.register(SubmissionReceipt , SubmissionReceiptAdmin)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('submitter_code',
                    'origin_code', 
                    'duplicate_payload', 
                    'contributor_codes',
                    'transaction_type',
                    'person_id',
                    'person_id_issuer', 
                     'status',)
    search_fields = ('origin_code', 'submitter__code', 'transaction_type__code', 
                     'destination__code', 'status_url', 'status')
admin.site.register(Submission, SubmissionAdmin)
