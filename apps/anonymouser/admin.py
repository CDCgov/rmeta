from django.contrib import admin
from .models import AnonymizedMessage



class AnonymizedMessageAdmin(admin.ModelAdmin):
    list_display = ('random_id', 'patient_age', 'patient_sex', 'updated')
    search_fields = ('random_id', )
admin.site.register(AnonymizedMessage, AnonymizedMessageAdmin)
