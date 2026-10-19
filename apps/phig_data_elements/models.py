"""PHIG workbook metadata, with one concrete table per data worksheet."""

from django.db import models


class DataElement(models.Model):
    name = models.CharField("Use case data element name", max_length=255)
    field_name = models.CharField(
        max_length=255, unique=True,
        help_text="Stable identifier, for example PatientFirstName.",
    )
    section = models.CharField(max_length=255, blank=True)
    source_row = models.PositiveIntegerField(null=True, blank=True)
    uscdi_element = models.TextField("USCDI v3.1 element", blank=True)
    rationale_for_inclusion = models.TextField(blank=True)
    base_fhir_profile = models.TextField("Base FHIR profile", blank=True)
    profile_data_element = models.TextField(blank=True)
    ig_must_support = models.TextField("IG must support?", blank=True)
    ig_cardinality = models.TextField("IG cardinality", blank=True)
    ig_value_set = models.TextField(
        "IG value set, other value set if applicable", blank=True,
    )
    value_set_name = models.TextField(blank=True)
    value_set_oid = models.TextField("Value set OID", blank=True)
    code_systems_name = models.TextField("Code system(s) name", blank=True)
    notes = models.TextField(blank=True)
    piqi_attributes = models.ManyToManyField(
        "piqi_pcm.Attribute", blank=True,
        related_name="phig_%(class)s_elements",
        help_text="Corresponding PIQI attributes; composite elements can have several.",
    )
    piqi_mapping_notes = models.TextField(blank=True)

    class Meta:
        abstract = True
        ordering = ("source_row", "name")

    def __str__(self):
        return self.name


class FoundationalDataset(DataElement):
    class Meta(DataElement.Meta):
        verbose_name = "Foundational dataset element"
        verbose_name_plural = "Foundational Dataset"


class FoundationalMustSupport(DataElement):
    class Meta(DataElement.Meta):
        verbose_name = "Foundational must support element"
        verbose_name_plural = "Foundational Must Support"


class MaternalChildDataset(DataElement):
    class Meta(DataElement.Meta):
        verbose_name = "Maternal child dataset element"
        verbose_name_plural = "Maternal Child Dataset"


class MaternalChildMustSupport(DataElement):
    class Meta(DataElement.Meta):
        verbose_name = "Maternal child must support element"
        verbose_name_plural = "Maternal Child Must Support"


class ChronicCareDataset(DataElement):
    class Meta(DataElement.Meta):
        verbose_name = "Chronic care dataset element"
        verbose_name_plural = "Chronic Care Dataset"


class ChronicCareMustSupport(DataElement):
    class Meta(DataElement.Meta):
        verbose_name = "Chronic care must support element"
        verbose_name_plural = "Chronic Care Must Support"


SHEET_MODELS = {
    "Foundational Dataset": FoundationalDataset,
    "Foundational Must Support": FoundationalMustSupport,
    "Maternal Child Dataset": MaternalChildDataset,
    "Maternal Child Must Support": MaternalChildMustSupport,
    "Chronic Care Dataset": ChronicCareDataset,
    "Chronic Care Must Support": ChronicCareMustSupport,
}
