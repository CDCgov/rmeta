from django.contrib import admin
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.html import format_html_join

from apps.piqi_pcm.models import Attribute

from .models import ReccomendedElement, SHEET_MODELS, UseCase

@admin.register(UseCase)
class UseCaseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "description")


class DataElementAdmin(admin.ModelAdmin):
    list_display = (
        "name", "section", "piqi_mnemonics", "uscdi_element", "ig_must_support",
    )
    search_fields = (
        "name", "field_name", "section", "uscdi_element", "profile_data_element",
        "value_set_name", "value_set_oid", "notes", "piqi_mapping_notes",
        "piqi_attributes__mnemonic", "piqi_attributes__field_name",
    )
    list_filter = ("section", "piqi_attributes__data_class")
    autocomplete_fields = ("piqi_attributes",)
    readonly_fields = ("source_row", "piqi_mnemonics")
    fieldsets = (
        (None, {"fields": ("name", "field_name", "section", "source_row")}),
        ("PIQI mapping", {"fields": (
            "piqi_mnemonics", "piqi_attributes", "piqi_mapping_notes",
        )}),
        ("Workbook metadata", {"fields": (
            "uscdi_element", "rationale_for_inclusion", "base_fhir_profile",
            "profile_data_element", "ig_must_support", "ig_cardinality",
            "ig_value_set", "value_set_name", "value_set_oid", "code_systems_name",
            "notes",
        )}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            Prefetch(
                "piqi_attributes",
                queryset=Attribute.objects.select_related("data_class"),
            )
        )

    @admin.display(description="PIQI mnemonic(s)")
    def piqi_mnemonics(self, obj):
        if obj.pk is None:
            return ""
        return format_html_join(
            ", ", '<a href="{}">{}</a>',
            (
                (
                    reverse("admin:piqi_pcm_attribute_change", args=(attribute.pk,)),
                    attribute.mnemonic,
                )
                for attribute in obj.piqi_attributes.all()
            ),
        )


for model in SHEET_MODELS.values():
    admin.site.register(model, DataElementAdmin)


@admin.register(ReccomendedElement)
class ReccomendedElementAdmin(DataElementAdmin):
    list_display = (
        "name", "field_name", "sheet_model", "section", "piqi_mnemonics",
        "uscdi_element", "uscdi_url",
    )
    list_filter = ("sheet_model",) + DataElementAdmin.list_filter
    search_fields = DataElementAdmin.search_fields + (
        "uscdi_url", "other_urls", "uscdi_data_elements__name",
        "message_mapping_guides__name", "message_mapping_guides__code",
        "hl7v2_messages__code", "hl7v2_segments__code",
        "code_references__name", "code_references__oid",
    )
    autocomplete_fields = DataElementAdmin.autocomplete_fields + (
        "uscdi_data_elements", "message_mapping_guides", "hl7v2_messages",
        "hl7v2_segments", "code_references",
    )
    fieldsets = (
        (None, {"fields": (
            "name", "field_name", "sheet_model", "section", "source_row",
        )}),
        *DataElementAdmin.fieldsets[1:],
        ("USCDI and reference links", {"fields": (
            "uscdi_data_elements", "uscdi_url", "other_urls", "code_references",
        )}),
        ("HL7v2 and message mapping guides", {"fields": (
            "message_mapping_guides", "hl7v2_messages", "hl7v2_segments",
            "hl7v2_url", "hl7v2_example",
        )}),
        ("FHIR", {"fields": ("fhir_url", "fhir_example")}),
        ("CDA", {"fields": ("cda_url", "cda_example")}),
        ("CSV", {"fields": ("csv_url", "csv_example")}),
    )
