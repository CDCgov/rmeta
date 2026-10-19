from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import (
    Attribute,
    AttributeRole,
    ClinicalModel,
    CoverageAttribute,
    DataClass,
    DemographicsAttribute,
)


class LoadPiqiPcmTests(TestCase):
    def test_import_is_idempotent_and_sheet_views_are_scoped(self):
        output = StringIO()
        call_command("load_piqi_pcm", stdout=output)
        call_command("load_piqi_pcm", stdout=output)

        self.assertEqual(ClinicalModel.objects.count(), 1)
        self.assertEqual(DataClass.objects.count(), 19)
        self.assertEqual(Attribute.objects.count(), 244)
        self.assertEqual(AttributeRole.objects.count(), 45)
        self.assertEqual(DemographicsAttribute.objects.count(), 20)
        self.assertEqual(CoverageAttribute.objects.count(), 15)

        model = ClinicalModel.objects.get(mnemonic="PAT_CLINICAL_V1")
        self.assertEqual(model.root_entity_mnemonic, "PATIENT")
        demographics = model.data_classes.get(mnemonic="DEM")
        self.assertEqual(demographics.icon, "fa-solid fa-id-card-clip")
        self.assertEqual(demographics.cardinality_mnemonic, "ONE")
        birth_date = demographics.attributes.get(mnemonic="DEM_DOB")
        self.assertTrue(
            birth_date.roles.filter(role_type_mnemonic="START_DATETIME").exists()
        )

