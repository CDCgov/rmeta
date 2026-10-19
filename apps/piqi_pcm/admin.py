from django.contrib import admin

from . import models


@admin.register(models.ClinicalModel)
class ClinicalModelAdmin(admin.ModelAdmin):
    list_display = ("name", "mnemonic", "version", "model_type_name", "root_entity_name")
    search_fields = ("name", "mnemonic", "description", "root_entity_name")
    list_filter = ("version", "model_type_name")


class AttributeInline(admin.TabularInline):
    model = models.Attribute
    fields = ("sequence", "name", "mnemonic", "field_name", "attribute_type_name")
    show_change_link = True
    extra = 0


@admin.register(models.DataClass)
class DataClassAdmin(admin.ModelAdmin):
    list_display = (
        "sequence", "name", "mnemonic", "clinical_model", "field_name",
        "cardinality_name", "is_inherited",
    )
    list_display_links = ("name",)
    list_filter = ("clinical_model", "cardinality_name", "is_inherited")
    search_fields = ("name", "mnemonic", "field_name", "description")
    ordering = ("clinical_model", "sequence")
    list_select_related = ("clinical_model",)
    autocomplete_fields = ("clinical_model",)
    inlines = (AttributeInline,)


class AttributeRoleInline(admin.TabularInline):
    model = models.AttributeRole
    fields = ("role_type_name", "role_type_mnemonic")
    extra = 0


@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = (
        "sequence", "name", "mnemonic", "data_class", "field_name",
        "attribute_type_name", "auto_generated",
    )
    list_display_links = ("name",)
    list_filter = ("data_class", "attribute_type_name", "auto_generated", "is_inherited")
    search_fields = (
        "name", "mnemonic", "field_name", "description",
        "data_class__name", "data_class__clinical_model__name",
    )
    ordering = ("data_class__clinical_model", "data_class__sequence", "sequence")
    list_select_related = ("data_class",)
    autocomplete_fields = ("data_class",)
    inlines = (AttributeRoleInline,)


class WorksheetAttributeAdmin(AttributeAdmin):
    """An attribute list and editor limited to one workbook worksheet."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "data_class":
            kwargs["queryset"] = models.DataClass.objects.filter(
                mnemonic=self.model.data_class_mnemonic
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        data_classes = models.DataClass.objects.filter(
            mnemonic=self.model.data_class_mnemonic
        )
        if data_classes.count() == 1:
            initial["data_class"] = data_classes.first().pk
        return initial


for proxy_model in (
    models.DemographicsAttribute,
    models.AllergiesAttribute,
    models.ConditionsAttribute,
    models.ImmunizationsAttribute,
    models.LabResultsAttribute,
    models.MedicationsAttribute,
    models.ProceduresAttribute,
    models.VitalSignsAttribute,
    models.DiagnosticImagingAttribute,
    models.MedicalDevicesAttribute,
    models.HealthAssessmentsAttribute,
    models.ClinicalDocumentsAttribute,
    models.EncountersAttribute,
    models.GoalsAttribute,
    models.CarePlansAttribute,
    models.PractitionersAttribute,
    models.ClinicalTestsAttribute,
    models.CoverageAttribute,
    models.ProvenanceAttribute,
):
    admin.site.register(proxy_model, WorksheetAttributeAdmin)


@admin.register(models.AttributeRole)
class AttributeRoleAdmin(admin.ModelAdmin):
    list_display = ("role_type_name", "role_type_mnemonic", "attribute", "data_class")
    list_filter = ("role_type_mnemonic", "attribute__data_class")
    search_fields = (
        "role_type_name", "role_type_mnemonic",
        "attribute__name", "attribute__mnemonic",
        "attribute__data_class__name",
    )
    list_select_related = ("attribute", "attribute__data_class")
    autocomplete_fields = ("attribute",)

    @admin.display(description="Data class", ordering="attribute__data_class__name")
    def data_class(self, obj):
        return obj.attribute.data_class

