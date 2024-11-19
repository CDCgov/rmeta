from django.contrib import admin
from .models import DataStream, Incomming


class DataStreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'application') 


admin.site.register(DataStream, DataStreamAdmin)

class IncommingAdmin(admin.ModelAdmin):
    list_display = ('data_stream', 'origin_agency_identifier', 
                    'intermediate_agency_identifier', 
                    'destination_agency_identifier', 'payload_type')

admin.site.register(Incomming, IncommingAdmin)
