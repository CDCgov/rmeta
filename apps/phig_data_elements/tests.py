from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from xml.etree import ElementTree
from zipfile import ZipFile

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from apps.piqi_pcm.models import Attribute, ClinicalModel, DataClass, DemographicsAttribute
from apps.uscdi.models import (
    CodeReference, DataClassType, DataElement as USCDIDataElement, DomainType,
    HL7Message, HL7Segment, MessageMappingGuide, UseCaseType,
)

from .management.commands.load_phig_data_elements import DEFAULT_WORKBOOK, XML_NS
from .models import (
    FoundationalDataset, FoundationalMustSupport, ReccomendedElement, SHEET_MODELS,
)
from .piqi_mappings import PIQI_MAPPINGS


class LoadPhigDataElementsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("load_piqi_pcm", stdout=StringIO())

    def assert_no_elements(self):
        for model in (*SHEET_MODELS.values(), ReccomendedElement):
            self.assertFalse(model.objects.exists())

    def edited_workbook(self, directory, member, edit):
        destination = Path(directory) / "edited.xlsx"
        with ZipFile(DEFAULT_WORKBOOK) as original, ZipFile(destination, "w") as edited:
            for info in original.infolist():
                data = original.read(info.filename)
                if info.filename == member:
                    root = ElementTree.fromstring(data)
                    edit(root)
                    data = ElementTree.tostring(root)
                edited.writestr(info, data)
        return destination

    @staticmethod
    def set_inline_cell(root, reference, text):
        namespace = "{" + XML_NS["x"] + "}"
        row_number = "".join(char for char in reference if char.isdigit())
        row = root.find(f"x:sheetData/x:row[@r='{row_number}']", XML_NS)
        cell = row.find(f"x:c[@r='{reference}']", XML_NS)
        if cell is None:
            cell = ElementTree.SubElement(row, namespace + "c")
        cell.clear()
        cell.set("r", reference)
        cell.set("t", "inlineStr")
        inline = ElementTree.SubElement(cell, namespace + "is")
        ElementTree.SubElement(inline, namespace + "t").text = text

    def test_real_workbook_import_is_idempotent_with_relational_mappings(self):
        output = StringIO()
        call_command("load_phig_data_elements", stdout=output)
        first = FoundationalDataset.objects.get(field_name="PatientFirstName")
        master = ReccomendedElement.objects.get(
            sheet_model="FoundationalDataset", field_name=first.field_name,
        )
        call_command("load_phig_data_elements", stdout=output)
        self.assertEqual(
            [model.objects.count() for model in SHEET_MODELS.values()],
            [39, 20, 18, 13, 1, 0],
        )
        self.assertEqual(first.pk, FoundationalDataset.objects.get(field_name="PatientFirstName").pk)
        self.assertEqual(ReccomendedElement.objects.count(), 91)
        self.assertEqual(master.pk, ReccomendedElement.objects.get(
            sheet_model="FoundationalDataset", field_name=first.field_name,
        ).pk)
        for model in SHEET_MODELS.values():
            for source in model.objects.all():
                copied = ReccomendedElement.objects.get(
                    sheet_model=model.__name__, field_name=source.field_name,
                )
                for field in model._meta.fields:
                    if not field.primary_key:
                        self.assertEqual(getattr(copied, field.name), getattr(source, field.name))
                self.assertEqual(
                    set(copied.piqi_attributes.values_list("pk", flat=True)),
                    set(source.piqi_attributes.values_list("pk", flat=True)),
                )
        self.assertEqual(first.name, "Patient First Name")
        self.assertEqual(first.section, "Patient")
        self.assertEqual(first.source_row, 4)
        self.assertEqual(first.profile_data_element, "Patient.name.given")
        self.assertEqual(first.piqi_attributes.get(), DemographicsAttribute.objects.get(field_name="firstName"))
        self.assertEqual(first.piqi_attributes.get().mnemonic, "DEM_FIRSTNAME")
        self.assertEqual(first.piqi_attributes.get().phig_foundationaldataset_elements.get(), first)
        address = FoundationalDataset.objects.get(field_name="PatientAddress")
        self.assertIn("2.16.840.1.113883.3.88.12.80.1", address.value_set_oid)
        self.assertIn("FHIR AddressUse", address.code_systems_name)
        self.assertIn("If homeless", address.notes)
        self.assertIn("district", address.ig_cardinality)
        self.assertEqual(
            set(FoundationalDataset.objects.get(field_name="EncounterTime").piqi_attributes.values_list("mnemonic", flat=True)),
            {"ENC_STARTDATE", "ENC_ENDDATETIME"},
        )
        sex = FoundationalDataset.objects.get(field_name="Sex")
        self.assertFalse(sex.piqi_attributes.exists())
        self.assertIn("birthSex", sex.piqi_mapping_notes)
        quantity = FoundationalMustSupport.objects.get(field_name="QuantityDispensed")
        self.assertFalse(quantity.piqi_attributes.exists())
        self.assertIn("not the amount dispensed", quantity.piqi_mapping_notes)
        for sheet, mappings in PIQI_MAPPINGS.items():
            self.assertFalse(set(mappings) - set(SHEET_MODELS[sheet].objects.values_list("field_name", flat=True)))
        self.assertIn("Imported 91 PHIG elements across 6 worksheets", output.getvalue())

    def test_refresh_reads_inline_cells_and_updates_existing_records(self):
        call_command("load_phig_data_elements", stdout=StringIO())
        first = FoundationalDataset.objects.get(field_name="PatientFirstName")
        master = ReccomendedElement.objects.get(
            sheet_model="FoundationalDataset", field_name=first.field_name,
        )
        master.uscdi_url = "https://example.org/uscdi/first-name"
        master.fhir_example = '{"given": ["Example"]}'
        master.save()
        guide = MessageMappingGuide.objects.create(name="Custom guide", code="CUSTOM")
        master.message_mapping_guides.add(guide)
        with TemporaryDirectory() as directory:
            source = self.edited_workbook(
                directory, "xl/worksheets/sheet2.xml",
                lambda root: self.set_inline_cell(root, "L4", "Updated workbook note"),
            )
            call_command("load_phig_data_elements", source=source, stdout=StringIO())
        first.refresh_from_db()
        self.assertEqual(first.notes, "Updated workbook note")
        self.assertEqual(FoundationalDataset.objects.count(), 39)
        self.assertEqual(first.piqi_attributes.count(), 1)
        master.refresh_from_db()
        self.assertEqual(master.notes, "Updated workbook note")
        self.assertEqual(master.uscdi_url, "https://example.org/uscdi/first-name")
        self.assertEqual(master.fhir_example, '{"given": ["Example"]}')
        self.assertEqual(master.message_mapping_guides.get(), guide)
        self.assertEqual(ReccomendedElement.objects.count(), 91)

    def test_dry_run_performs_validation_without_writing(self):
        output = StringIO()
        call_command("load_phig_data_elements", dry_run=True, stdout=output)
        self.assert_no_elements()
        self.assertIn("Would import 91", output.getvalue())

    def test_missing_piqi_model_is_actionable_and_does_not_write(self):
        with self.assertRaisesMessage(CommandError, "load_piqi_pcm"):
            call_command("load_phig_data_elements", piqi_model="NOT_LOADED", stdout=StringIO())
        self.assert_no_elements()

    def test_missing_or_ambiguous_piqi_attribute_does_not_write(self):
        first = Attribute.objects.get(mnemonic="DEM_FIRSTNAME")
        first.delete()
        with self.assertRaisesMessage(CommandError, "DEM_FIRSTNAME"):
            call_command("load_phig_data_elements", stdout=StringIO())
        self.assert_no_elements()
        for data_class in DataClass.objects.filter(mnemonic__in=("DEM", "CND")):
            Attribute.objects.create(
                data_class=data_class, mnemonic="DEM_FIRSTNAME", name="firstName",
                field_name="firstName", sequence=100, attribute_type_name="String",
            )
        with self.assertRaisesMessage(CommandError, "ambiguous PIQI attributes"):
            call_command("load_phig_data_elements", stdout=StringIO())
        self.assert_no_elements()

    def test_piqi_relationships_are_scoped_to_the_selected_clinical_model(self):
        alternate = ClinicalModel.objects.create(
            name="Alternate", mnemonic="ALTERNATE", version=2, model_type_name="Clinical",
        )
        data_class = DataClass.objects.create(
            clinical_model=alternate, name="Demographics", mnemonic="DEM", sequence=1,
        )
        Attribute.objects.create(
            data_class=data_class, name="firstName", mnemonic="DEM_FIRSTNAME",
            field_name="firstName", sequence=1, attribute_type_name="String",
        )
        with self.assertRaisesMessage(CommandError, "Missing or ambiguous PIQI attributes"):
            call_command("load_phig_data_elements", piqi_model="ALTERNATE", stdout=StringIO())
        self.assert_no_elements()
        call_command("load_phig_data_elements", stdout=StringIO())
        first = FoundationalDataset.objects.get(field_name="PatientFirstName")
        self.assertEqual(first.piqi_attributes.get().data_class.clinical_model.mnemonic, "PAT_CLINICAL_V1")

    def test_duplicate_element_in_workbook_is_rejected_before_writing(self):
        with TemporaryDirectory() as directory:
            source = self.edited_workbook(
                directory, "xl/worksheets/sheet2.xml",
                lambda root: self.set_inline_cell(root, "A4", "Patient Last Name"),
            )
            with self.assertRaisesMessage(CommandError, "duplicate or invalid identifier"):
                call_command("load_phig_data_elements", source=source, stdout=StringIO())
        self.assert_no_elements()

    def test_missing_sheet_or_invalid_header_is_rejected_before_writing(self):
        def remove_sheet(root):
            sheets = root.find("x:sheets", XML_NS)
            sheets.remove(sheets[-1])

        edits = (
            ("xl/workbook.xml", remove_sheet, "Missing PHIG worksheets"),
            ("xl/worksheets/sheet2.xml", lambda root: self.set_inline_cell(root, "A1", "Wrong header"), "unexpected columns"),
        )
        for member, edit, message in edits:
            with self.subTest(message=message), TemporaryDirectory() as directory:
                source = self.edited_workbook(directory, member, edit)
                with self.assertRaisesMessage(CommandError, message):
                    call_command("load_phig_data_elements", source=source, stdout=StringIO())
                self.assert_no_elements()

    def test_import_rolls_back_all_sheets_on_late_database_failure(self):
        with patch.object(FoundationalMustSupport.objects, "update_or_create", side_effect=IntegrityError("Simulated failure")):
            with self.assertRaises(IntegrityError):
                call_command("load_phig_data_elements", stdout=StringIO())
        self.assert_no_elements()

    def test_all_sheet_admins_render_searchable_piqi_links(self):
        call_command("load_phig_data_elements", stdout=StringIO())
        user = get_user_model().objects.create_superuser(username="phig-admin", password="test-password")
        self.client.force_login(user)
        for model in (*SHEET_MODELS.values(), ReccomendedElement):
            self.assertTrue(admin.site.is_registered(model))
            response = self.client.get(reverse(f"admin:phig_data_elements_{model._meta.model_name}_changelist"))
            self.assertEqual(response.status_code, 200)
        first = FoundationalDataset.objects.get(field_name="PatientFirstName")
        attribute = first.piqi_attributes.get()
        response = self.client.get(
            reverse("admin:phig_data_elements_foundationaldataset_changelist"),
            {"q": "DEM_FIRSTNAME"},
        )
        self.assertContains(response, "Patient First Name")
        self.assertContains(response, f'<a href="{reverse("admin:piqi_pcm_attribute_change", args=(attribute.pk,))}">DEM_FIRSTNAME</a>', html=True)
        self.assertNotContains(response, "Patient Last Name")
        response = self.client.get(reverse("admin:phig_data_elements_foundationaldataset_change", args=(first.pk,)))
        self.assertContains(response, "DEM_FIRSTNAME")


class ReccomendedElementTests(TestCase):
    def test_identifier_is_unique_within_a_sheet_and_sheet_choice_is_validated(self):
        values = {"name": "Patient first name", "field_name": "PatientFirstName"}
        ReccomendedElement.objects.create(sheet_model="FoundationalDataset", **values)
        ReccomendedElement.objects.create(sheet_model="MaternalChildDataset", **values)
        with transaction.atomic(), self.assertRaises(IntegrityError):
            ReccomendedElement.objects.create(sheet_model="FoundationalDataset", **values)
        with self.assertRaises(ValidationError):
            ReccomendedElement(sheet_model="UnknownWorksheet", **values).full_clean()

    def test_admin_saves_references_urls_and_multiline_examples(self):
        clinical_model = ClinicalModel.objects.create(
            name="Test", mnemonic="TEST", version=1, model_type_name="Clinical",
        )
        data_class = DataClass.objects.create(
            clinical_model=clinical_model, name="Demographics", mnemonic="DEM", sequence=1,
        )
        attribute = Attribute.objects.create(
            data_class=data_class, name="First name", mnemonic="DEM_FIRSTNAME",
            field_name="firstName", sequence=1, attribute_type_name="String",
        )
        uscdi = USCDIDataElement.objects.create(
            name="First name", code="FIRST_NAME",
            domain=DomainType.objects.create(name="Clinical", code="CLINICAL"),
            data_class=DataClassType.objects.create(name="Demographics", code="DEM"),
            use_case=UseCaseType.objects.create(name="General", code="GENERAL"),
        )
        guide = MessageMappingGuide.objects.create(name="Minimum guide", code="MINIMUM")
        message = HL7Message.objects.create(name="Patient update", code="ADT_A08")
        segment = HL7Segment.objects.create(name="Patient identification", code="PID")
        code_reference = CodeReference.objects.create(
            name="Names", title="Names", oid="1.2.3", status="active",
            url="https://example.org/codes/names",
        )
        data = {
            "name": "Patient first name", "field_name": "PatientFirstName",
            "sheet_model": "FoundationalDataset", "piqi_attributes": [attribute.pk],
            "uscdi_data_elements": [uscdi.pk], "message_mapping_guides": [guide.pk],
            "hl7v2_messages": [message.pk], "hl7v2_segments": [segment.pk],
            "code_references": [code_reference.pk],
            "uscdi_url": "https://example.org/uscdi/first-name",
            "other_urls": "https://example.org/one\nhttps://example.org/two",
        }
        examples = {
            "hl7v2": "MSH|^~\\&|EXAMPLE\nPID|1||12345",
            "fhir": '{\n  "given": ["Example"]\n}',
            "cda": "<name>\n<given>Example</given>\n</name>",
            "csv": "first_name,last_name\nExample,Patient",
        }
        for format_name, example in examples.items():
            data[f"{format_name}_url"] = f"https://example.org/{format_name}"
            data[f"{format_name}_example"] = example
        user = get_user_model().objects.create_superuser(
            username="master-admin", password="test-password",
        )
        self.client.force_login(user)
        response = self.client.post(reverse("admin:phig_data_elements_reccomendedelement_add"), data)
        self.assertEqual(response.status_code, 302)
        master = ReccomendedElement.objects.get()
        for field in (
            "piqi_attributes", "uscdi_data_elements", "message_mapping_guides",
            "hl7v2_messages", "hl7v2_segments", "code_references",
        ):
            self.assertEqual(list(getattr(master, field).values_list("pk", flat=True)), data[field])
        self.assertEqual(master.uscdi_url, data["uscdi_url"])
        self.assertEqual(master.other_urls, data["other_urls"])
        for format_name, example in examples.items():
            self.assertEqual(getattr(master, f"{format_name}_url"), data[f"{format_name}_url"])
            self.assertEqual(getattr(master, f"{format_name}_example"), example)
        response = self.client.get(
            reverse("admin:phig_data_elements_reccomendedelement_changelist"),
            {"q": "DEM_FIRSTNAME", "sheet_model__exact": "FoundationalDataset"},
        )
        self.assertContains(response, master.name)
        response = self.client.get(
            reverse("admin:phig_data_elements_reccomendedelement_change", args=(master.pk,)),
        )
        self.assertContains(response, "Minimum guide")
        self.assertContains(response, "first_name,last_name")


class ReccomendedElementMigrationTests(TransactionTestCase):
    def test_migration_copies_every_sheet_and_preserves_piqi_and_metadata(self):
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        previous = [("phig_data_elements", "0001_initial")]
        executor.migrate(previous)
        self.addCleanup(lambda: MigrationExecutor(connection).migrate(latest))
        old_apps = executor.loader.project_state(previous).apps
        clinical_model = old_apps.get_model("piqi_pcm", "ClinicalModel").objects.create(
            name="Migration test", mnemonic="MIGRATION", version=1, model_type_name="Clinical",
        )
        data_class = old_apps.get_model("piqi_pcm", "DataClass").objects.create(
            clinical_model=clinical_model, name="Demographics", mnemonic="DEM", sequence=1,
        )
        attribute = old_apps.get_model("piqi_pcm", "Attribute").objects.create(
            data_class=data_class, name="First name", mnemonic="DEM_FIRSTNAME",
            field_name="firstName", sequence=1, attribute_type_name="String",
        )
        expected = {}
        for model_name in (model.__name__ for model in SHEET_MODELS.values()):
            source_model = old_apps.get_model("phig_data_elements", model_name)
            values = {
                field.name: f"{model_name}: {field.name}"
                for field in source_model._meta.fields
                if not field.primary_key and field.name != "source_row"
            }
            values.update(field_name="PatientFirstName", source_row=4)
            source = source_model.objects.create(**values)
            source.piqi_attributes.add(attribute)
            expected[model_name] = values
        executor = MigrationExecutor(connection)
        executor.migrate(latest)
        new_apps = executor.loader.project_state(latest).apps
        master_model = new_apps.get_model("phig_data_elements", "ReccomendedElement")
        self.assertEqual(master_model.objects.count(), 6)
        for model_name, values in expected.items():
            master = master_model.objects.get(sheet_model=model_name)
            for field, value in values.items():
                self.assertEqual(getattr(master, field), value)
            self.assertEqual(list(master.piqi_attributes.values_list("pk", flat=True)), [attribute.pk])
            self.assertTrue(old_apps.get_model("phig_data_elements", model_name).objects.exists())
