from django.contrib import admin
from .models import DataElement

class DataElementAdmin(admin.ModelAdmin):
    list_display = ('code', 'common_name', 'code_display', 'code_system', 'name', 'code_system_version')
    search_fields = ('common_name', 'name', 'code', 'code_display', 'code_system', 'code_system_version')
    list_filter = ('common_name', 'code', 'code_display', 'code_system', 'code_system_version')
    ordering = ('common_name', 'code', 'code_display', 'code_system', 'code_system_version')

admin.site.register(DataElement, DataElementAdmin)
