from django.contrib import admin
from .models import DataElementType, DomainType, DataClassType, UseCaseType


class DataElementTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 
                    'data_class', 'use_case', 'description',
                    'additional_information',
                    'in_uscdi', 'uscdi_url',
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
