"""Metadata for the PIQI Patient Clinical Model workbook and JSON export.

The attribute worksheets share one schema. Their proxy models give each sheet a
separate admin view while keeping attributes in one table for cross-sheet links.
"""

from django.db import models


class ClinicalModel(models.Model):
    name = models.CharField(max_length=255)
    mnemonic = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    version = models.PositiveIntegerField()
    model_type_name = models.CharField(max_length=100)
    base_model = models.CharField(max_length=255, blank=True)
    root_entity_name = models.CharField(max_length=100, blank=True)
    root_entity_mnemonic = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("name", "version")
        verbose_name = "Patient clinical model"

    def __str__(self):
        return f"{self.name} (v{self.version})"


class DataClass(models.Model):
    clinical_model = models.ForeignKey(
        ClinicalModel, on_delete=models.CASCADE, related_name="data_classes"
    )
    name = models.CharField(max_length=255)
    mnemonic = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100, blank=True)
    field_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_inherited = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField()
    icon = models.CharField(max_length=255, blank=True)
    cardinality_name = models.CharField(max_length=100, blank=True)
    cardinality_mnemonic = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ("clinical_model", "sequence", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("clinical_model", "mnemonic"), name="piqi_class_mnemonic"
            ),
        ]
        verbose_name_plural = "Data classes"

    def __str__(self):
        return f"{self.name} ({self.mnemonic})"


class Attribute(models.Model):
    data_class = models.ForeignKey(
        DataClass, on_delete=models.CASCADE, related_name="attributes"
    )
    name = models.CharField(max_length=255)
    mnemonic = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100, blank=True)
    field_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    attribute_type_name = models.CharField(max_length=100)
    attribute_type_mnemonic = models.CharField(max_length=100, blank=True)
    is_inherited = models.BooleanField(default=False)
    sequence = models.PositiveIntegerField()
    auto_generated = models.BooleanField(default=False)

    class Meta:
        ordering = ("data_class", "sequence", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("data_class", "mnemonic"), name="piqi_attribute_mnemonic"
            ),
        ]

    def __str__(self):
        return f"{self.data_class.name}: {self.name}"


class AttributeRole(models.Model):
    """A JSON role assigned to an attribute in a data class."""

    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="roles"
    )
    role_type_name = models.CharField(max_length=100)
    role_type_mnemonic = models.CharField(max_length=100)

    class Meta:
        ordering = ("attribute", "role_type_name")
        constraints = [
            models.UniqueConstraint(
                fields=("attribute", "role_type_mnemonic"), name="piqi_attribute_role"
            )
        ]

    def __str__(self):
        return f"{self.role_type_name}: {self.attribute}"


class SheetAttributeManager(models.Manager):
    """Restrict a proxy model to the data class represented by its worksheet."""

    def get_queryset(self):
        return super().get_queryset().filter(
            data_class__mnemonic=self.model.data_class_mnemonic
        )


class DemographicsAttribute(Attribute):
    data_class_mnemonic = "DEM"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Demographics attribute"


class AllergiesAttribute(Attribute):
    data_class_mnemonic = "ALG"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Allergies attribute"


class ConditionsAttribute(Attribute):
    data_class_mnemonic = "CND"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Conditions attribute"


class ImmunizationsAttribute(Attribute):
    data_class_mnemonic = "IMM"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Immunizations attribute"


class LabResultsAttribute(Attribute):
    data_class_mnemonic = "LAB"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Lab Results attribute"


class MedicationsAttribute(Attribute):
    data_class_mnemonic = "MED"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Medications attribute"


class ProceduresAttribute(Attribute):
    data_class_mnemonic = "PRC"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Procedures attribute"


class VitalSignsAttribute(Attribute):
    data_class_mnemonic = "VIT"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Vital Signs attribute"


class DiagnosticImagingAttribute(Attribute):
    data_class_mnemonic = "IMAGING"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Diagnostic Imaging attribute"


class MedicalDevicesAttribute(Attribute):
    data_class_mnemonic = "DEV"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Medical Devices attribute"


class HealthAssessmentsAttribute(Attribute):
    data_class_mnemonic = "HA"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Health Assessments attribute"


class ClinicalDocumentsAttribute(Attribute):
    data_class_mnemonic = "DOC"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Clinical Documents attribute"


class EncountersAttribute(Attribute):
    data_class_mnemonic = "ENC"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Encounters attribute"


class GoalsAttribute(Attribute):
    data_class_mnemonic = "GOAL"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Goals attribute"


class CarePlansAttribute(Attribute):
    data_class_mnemonic = "CAREPLAN"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Care Plans attribute"


class PractitionersAttribute(Attribute):
    data_class_mnemonic = "PRACTITIONER"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Practitioners attribute"


class ClinicalTestsAttribute(Attribute):
    data_class_mnemonic = "CLINICAL_TESTS"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Clinical Tests attribute"


class CoverageAttribute(Attribute):
    data_class_mnemonic = "COVERAGE"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Coverage attribute"


class ProvenanceAttribute(Attribute):
    data_class_mnemonic = "PROVENANCE"
    objects = SheetAttributeManager()

    class Meta:
        proxy = True
        verbose_name = "Provenance attribute"

