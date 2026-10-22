"""PHIG workbook metadata and a master table of recommended elements."""

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

SHEET_MODEL_CHOICES = tuple(
    (model.__name__, sheet_name) for sheet_name, model in SHEET_MODELS.items()
)
class UseCase(models.Model):
    """A PHIG use case, which is a collection of recommended elements."""

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)


    class Meta:
        verbose_name = "Use case"
        verbose_name_plural = "Use cases"
        ordering = ("name",)

    def __str__(self):
        return self.code

class ReccomendedElement(DataElement):
    """A master PHIG row, identified by its source sheet and field name."""

    sheet_model = models.CharField(
        "Source worksheet", max_length=64, choices=SHEET_MODEL_CHOICES,
    )
    field_name = models.CharField(
        max_length=255,
        help_text="Stable identifier within the source worksheet, for example PatientFirstName.",
    )
    use_cases = models.ManyToManyField(UseCase, blank=True, 
                                       related_name="recommended_elements",)
    message_mapping_guides = models.ManyToManyField(
        "uscdi.MessageMappingGuide", blank=True, related_name="recommended_elements",
    )
    hl7v2_messages = models.ManyToManyField(
        "uscdi.HL7Message", verbose_name="HL7v2 messages",
        blank=True, related_name="recommended_elements",
    )
    hl7v2_segments = models.ManyToManyField(
        "uscdi.HL7Segment", verbose_name="HL7v2 segments",
        blank=True, related_name="recommended_elements",
    )
    uscdi_data_elements = models.ManyToManyField(
        "uscdi.DataElement", verbose_name="USCDI data elements",
        blank=True, related_name="recommended_elements",
    )
    code_references = models.ManyToManyField(
        "uscdi.CodeReference", blank=True, related_name="recommended_elements",
    )
    uscdi_url = models.URLField("USCDI URL", max_length=2048, blank=True)
    other_urls = models.TextField(
        "Other reference URLs", blank=True, help_text="One reference URL per line.",
    )
    hl7v2_url = models.URLField("HL7v2 URL", max_length=2048, blank=True)
    hl7v2_example = models.TextField("HL7v2 example", blank=True)
    fhir_url = models.URLField("FHIR URL", max_length=2048, blank=True)
    fhir_example = models.TextField("FHIR example", blank=True)
    cda_url = models.URLField("CDA URL", max_length=2048, blank=True)
    cda_example = models.TextField("CDA example", blank=True)
    csv_url = models.URLField("CSV URL", max_length=2048, blank=True)
    csv_example = models.TextField("CSV example", blank=True)

    class Meta(DataElement.Meta):
        verbose_name = "Recommended element"
        verbose_name_plural = "Recommended elements"
        ordering = ("sheet_model", "source_row", "name")
        constraints = [
            models.UniqueConstraint(
                fields=("sheet_model", "field_name"), name="phig_recommended_sheet_field",
            ),
        ]
