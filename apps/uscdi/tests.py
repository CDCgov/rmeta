import csv
import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.http import HttpResponse
from django.template.loader import get_template
from django.test import TestCase
from django.urls import reverse

from .management.commands.loaduscdi31dataelements import (
    _load_mmg_index,
    _select_mmg_mapping,
)
from .models import DataClassType, DataElement, DomainType, UseCaseType


CANONICAL_FIELDS = [
    "Classification Level",
    "Data Class",
    "Data Class Description",
    "Data Element",
    "Data Element Description",
    "Applicable Standards",
    "Submitter Name",
    "Submitter Organization",
    "Submission Date",
]

PUBLIC_HEALTH_FIELDS = [
    "Data Element Name",
    "Data Class Name",
    "Description",
    "Additional Information",
    "Current USCDI Level",
    "USCDI URL",
    "Applicable Vocabulary Standard(s)",
    "Associated IG or Profile URL(s)",
    "Associated US Core Profile URL(s)",
]


class LoadUSCDI31DataElementsTests(TestCase):
    def setUp(self):
        self.temporary_directory = TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)

    def tearDown(self):
        self.temporary_directory.cleanup()

    def write_csv(self, name, fieldnames, rows):
        path = self.directory / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def write_json(self, name, payload):
        path = self.directory / name
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle)
        return path

    def canonical_path(self):
        common = {
            "Classification Level": "USCDI V3.1",
            "Data Class": "Patient Demographics/Information",
            "Data Class Description": "Data used to categorize individuals.",
            "Applicable Standards": "Example standard&nbsp;2.72",
            "Submitter Organization": "ONC",
        }
        return self.write_csv(
            "uscdi.csv",
            CANONICAL_FIELDS,
            [
                {
                    **common,
                    "Data Element": "Date of Birth",
                    "Data Element Description": "The patient's date of birth.",
                    "Submitter Name": "First submitter",
                    "Submission Date": "2025-01-01",
                },
                {
                    # Same canonical content: only provenance differs.
                    **common,
                    "Data Element": "Date of Birth",
                    "Data Element Description": "The patient's date of birth.",
                    "Submitter Name": "Second submitter",
                    "Submission Date": "2026-01-01",
                },
                {
                    **common,
                    "Data Element": "First Name",
                    "Data Element Description": "The patient's first name.",
                    "Submitter Name": "ONC",
                    "Submission Date": "2025-01-01",
                },
            ],
        )

    def public_health_path(self):
        return self.write_csv(
            "public-health.csv",
            PUBLIC_HEALTH_FIELDS,
            [
                {
                    "Data Element Name": "Date of Birth",
                    "Data Class Name": "Patient Demographics",
                    "Description": "Legacy description",
                    "Additional Information": "Public health context",
                    "Current USCDI Level": "USCDI V4",
                    "USCDI URL": "https://www.healthit.gov/isa/taxonomy/term/736/uscdi-v4",
                    "Applicable Vocabulary Standard(s)": "Legacy vocabulary",
                    "Associated IG or Profile URL(s)": (
                        "https://hl7.org/fhir/us/ph-library/2022Sep/"
                        "StructureDefinition-us-ph-patient.html"
                    ),
                    "Associated US Core Profile URL(s)": (
                        "https://build.fhir.org/ig/HL7/US-Core/"
                        "StructureDefinition-us-core-patient.html"
                    ),
                },
                {
                    # This V4-only element must not be promoted into V3.1.
                    "Data Element Name": "Gender Identity",
                    "Data Class Name": "Patient Demographics",
                    "Description": "A V4-only element",
                    "Additional Information": "",
                    "Current USCDI Level": "USCDI V4",
                    "USCDI URL": "https://www.healthit.gov/isa/taxonomy/term/2736/uscdi-v4",
                    "Applicable Vocabulary Standard(s)": "",
                    "Associated IG or Profile URL(s)": "",
                    "Associated US Core Profile URL(s)": "",
                },
                {
                    # Same name in an incompatible class must not be merged.
                    "Data Element Name": "Date of Birth",
                    "Data Class Name": "Laboratory",
                    "Description": "Unrelated laboratory concept",
                    "Additional Information": "Must not be imported",
                    "Current USCDI Level": "Level 0",
                    "USCDI URL": "https://example.invalid/wrong-class",
                    "Applicable Vocabulary Standard(s)": "Wrong vocabulary",
                    "Associated IG or Profile URL(s)": "https://example.invalid/wrong-ig",
                    "Associated US Core Profile URL(s)": "https://example.invalid/wrong-core",
                },
            ],
        )

    def mmg_path(self):
        def guide(
            number,
            identifier,
            may_repeat,
            *,
            guide_name,
            guide_status,
            element_status="Final",
            segment="PID",
            field=7,
        ):
            return {
                "id": f"parent-guide-{number}",
                "name": guide_name,
                "guideStatus": guide_status,
                "isActive": True,
                "blocks": [
                    {
                        "id": f"parent-block-{number}",
                        "elements": [
                            {
                                "id": f"element-{number}",
                                "guideId": f"element-guide-{number}",
                                "guideInternalVersion": number,
                                "blockId": f"element-block-{number}",
                                "ordinal": number,
                                "name": "Birth Date",
                                "description": "MMG description",
                                "shortName": "date_of_birth",
                                "comments": "Comment",
                                "status": element_status,
                                "dataType": "Date",
                                "businessRules": "Rule",
                                "isUnitOfMeasure": False,
                                "codeSystem": "N/A",
                                "legacyPriority": "R",
                                "priority": "1",
                                "isRepeat": may_repeat.startswith("Y"),
                                "mayRepeat": may_repeat,
                                "valueSetCode": "",
                                "mappings": {
                                    "hl7v251": {
                                        "legacyIdentifier": "DEM127",
                                        "identifier": identifier,
                                        "messageContext": f"{segment}-{field}",
                                        "dataType": "TS",
                                        "segmentType": segment,
                                        "fieldPosition": field,
                                        "componentPosition": -1,
                                        "usage": "R",
                                        "cardinality": "[1..1]",
                                        "literalFieldValues": {"example": "value"},
                                        "repeatingGroupElementType": "NO",
                                        "sampleSegment": "PID|||||||20000101",
                                    }
                                },
                            }
                        ],
                    }
                ],
            }

        return self.write_json(
            "mmg.json",
            {
                "statusCode": 200,
                "result": [
                    guide(
                        1,
                        "N/A: PID-7",
                        "Y/3",
                        guide_name="Case Notification MDN",
                        guide_status="PeerReview",
                    ),
                    guide(
                        2,
                        "SECOND: PID-7",
                        "N",
                        guide_name="Generic v3.0 - full (Developer Testing)",
                        guide_status="Development",
                    ),
                    guide(
                        3,
                        "DEM115",
                        "N",
                        guide_name="Old disease guide",
                        guide_status="Development",
                        element_status="Development",
                        segment="OBX",
                        field=5,
                    ),
                ],
                "message": "OK",
            },
        )

    def command_options(self):
        return {
            "uscdi_csv": self.canonical_path(),
            "public_health_csv": self.public_health_path(),
            "mmg_json": self.mmg_path(),
        }

    def test_loads_one_row_per_canonical_element_and_selects_best_mapping(self):
        stdout = StringIO()
        call_command("loaduscdi31dataelements", stdout=stdout, **self.command_options())

        self.assertEqual(DataElement.objects.count(), 2)
        date_of_birth_rows = DataElement.objects.filter(data_element="Date of Birth")
        self.assertEqual(date_of_birth_rows.count(), 1)

        date_of_birth = date_of_birth_rows.get()
        self.assertEqual(date_of_birth.code, "USCDI-V3-1-736")
        self.assertEqual(date_of_birth.mm_name, "Birth Date")
        self.assertEqual(date_of_birth.hl7v2_identifier, "N/A: PID-7")
        self.assertEqual(date_of_birth.hl7v2_segment_type, "PID")
        self.assertEqual(date_of_birth.hl7v2_field_position, 7)
        self.assertEqual(date_of_birth.mm_mayRepeat, "Y/3")
        self.assertTrue(date_of_birth.mm_isRepeat)
        self.assertEqual(date_of_birth.mm_elementId, "element-1")
        self.assertEqual(date_of_birth.mm_containingGuideId, "parent-guide-1")
        self.assertEqual(date_of_birth.mm_containingGuideName, "Case Notification MDN")
        self.assertEqual(date_of_birth.mm_containingGuideStatus, "PeerReview")
        self.assertEqual(date_of_birth.mm_containingBlockId, "parent-block-1")
        self.assertEqual(date_of_birth.mm_matchMethod, "alias")
        self.assertGreater(date_of_birth.mm_matchScore, 0.9)
        self.assertEqual(date_of_birth.mm_guideId, "element-guide-1")
        self.assertEqual(date_of_birth.mm_blockId, "element-block-1")
        self.assertEqual(date_of_birth.hl7v2_component_position, -1)
        self.assertEqual(
            date_of_birth.hl7v2_literalFieldValues, '{"example":"value"}'
        )
        self.assertIsNone(date_of_birth.uscdi_uuid)
        self.assertEqual(date_of_birth.classification_level, "USCDI V3.1")
        self.assertEqual(
            date_of_birth.uscdi_url,
            "https://isp.healthit.gov/taxonomy/term/736/uscdi-v3-1",
        )
        self.assertEqual(
            date_of_birth.fhir_associated_ig_or_profile_urls,
            "https://hl7.org/fhir/us/ph-library/STU2/"
            "StructureDefinition-us-ph-patient.html",
        )
        self.assertEqual(
            date_of_birth.fhir_associated_us_core_profile_urls,
            "https://hl7.org/fhir/us/core/STU6.1/"
            "StructureDefinition-us-core-patient.html",
        )
        self.assertNotIn("example.invalid", date_of_birth.fhir_associated_ig_or_profile_urls)
        self.assertNotIn("Must not be imported", date_of_birth.additional_information)
        self.assertEqual(date_of_birth.applicable_standards, "Example standard 2.72")
        self.assertEqual(
            date_of_birth.applicable_vocabulary_standards, "Legacy vocabulary"
        )

        first_name = DataElement.objects.get(data_element="First Name")
        self.assertEqual(first_name.code, "USCDI-V3-1-706")
        self.assertEqual(first_name.mm_guideId, "")
        self.assertEqual(first_name.mm_matchMethod, "")
        self.assertIsNone(first_name.mm_matchScore)
        self.assertFalse(DataElement.objects.filter(name="Gender Identity").exists())
        self.assertEqual(first_name.data_class.name, "Patient Demographics/Information")
        self.assertEqual(first_name.domain.name, "USCDI")
        self.assertEqual(first_name.use_case.name, "USCDI V3.1")

        # Regression coverage for the new model property's former bad names.
        self.assertEqual(date_of_birth.as_dict["mm_guideId"], "element-guide-1")
        self.assertIn("fhir_associated_ig_or_profile_urls", date_of_birth.as_dict)

        output = stdout.getvalue()
        self.assertIn("Loaded 2 canonical USCDI V3.1 elements into 2 rows", output)
        self.assertIn("Collapsed 1 duplicate canonical row", output)
        self.assertIn("selected MMG mappings for 1 element(s)", output)
        self.assertIn("2 Public Health row(s) labeled USCDI V4", output)

    def test_rerun_is_idempotent(self):
        options = self.command_options()
        call_command("loaduscdi31dataelements", stdout=StringIO(), **options)
        codes = set(DataElement.objects.values_list("code", flat=True))

        stdout = StringIO()
        call_command("loaduscdi31dataelements", stdout=stdout, **options)

        self.assertEqual(DataElement.objects.count(), 2)
        self.assertEqual(set(DataElement.objects.values_list("code", flat=True)), codes)
        self.assertIn("0 created, 2 updated", stdout.getvalue())

    def test_rerun_updates_mapping_without_changing_canonical_code(self):
        options = self.command_options()
        call_command("loaduscdi31dataelements", stdout=StringIO(), **options)

        payload = json.loads(options["mmg_json"].read_text(encoding="utf-8"))
        moved_guide = payload["result"][1]
        moved_guide["blocks"][0]["elements"][0]["ordinal"] = 9
        updated_mmg = self.write_json(
            "updated-mmg.json", {**payload, "result": [moved_guide]}
        )

        stdout = StringIO()
        call_command(
            "loaduscdi31dataelements",
            stdout=stdout,
            **{**options, "mmg_json": updated_mmg},
        )

        self.assertEqual(DataElement.objects.count(), 2)
        moved = DataElement.objects.get(data_element="Date of Birth")
        self.assertEqual(moved.code, "USCDI-V3-1-736")
        self.assertEqual(moved.mm_ordinal, 9)
        self.assertEqual(moved.hl7v2_identifier, "SECOND: PID-7")
        self.assertIn("0 created, 2 updated", stdout.getvalue())

    def test_replace_removes_rows_outside_the_loader_namespace(self):
        options = self.command_options()
        call_command("loaduscdi31dataelements", stdout=StringIO(), **options)
        existing = DataElement.objects.first()
        DataElement.objects.create(
            code="manual-row",
            name="Manual row",
            domain=existing.domain,
            data_class=existing.data_class,
            use_case=existing.use_case,
        )

        stdout = StringIO()
        call_command(
            "loaduscdi31dataelements",
            replace=True,
            stdout=stdout,
            **options,
        )

        self.assertEqual(DataElement.objects.count(), 2)
        self.assertFalse(DataElement.objects.filter(code="manual-row").exists())
        self.assertIn("Replacement mode removed 3 pre-existing DataElement row(s)", stdout.getvalue())

    def test_fuzzy_matching_requires_a_high_score_and_clear_margin(self):
        source_index = _load_mmg_index(self.mmg_path())
        occurrence = source_index["birth date"][0]
        canonical_name = "One Two Three Four Five Six Seven Eight Nine Ten"
        clear_index = {
            "one two three four five six seven eight nine ten eleven": [occurrence],
            "completely unrelated candidate": [occurrence],
        }

        mapping, method, score, _ = _select_mmg_mapping(
            canonical_name, clear_index
        )
        self.assertIs(mapping, occurrence)
        self.assertEqual(method, "fuzzy")
        self.assertGreaterEqual(score, 0.9)

        ambiguous_index = {
            **clear_index,
            "one two three four five six seven eight nine ten twelve": [occurrence],
        }
        mapping, method, score, count = _select_mmg_mapping(
            canonical_name, ambiguous_index
        )
        self.assertIsNone(mapping)
        self.assertEqual((method, score, count), ("", 0.0, 0))

    def test_bundled_sources_load_the_complete_v31_inventory(self):
        stdout = StringIO()
        call_command("loaduscdi31dataelements", stdout=stdout)

        self.assertEqual(
            DataElement.objects.values("data_class", "data_element").distinct().count(),
            92,
        )
        self.assertEqual(DataElement.objects.count(), 92)
        self.assertGreater(DataElement.objects.exclude(mm_guideId="").count(), 7)
        self.assertFalse(
            DataElement.objects.exclude(classification_level="USCDI V3.1").exists()
        )
        self.assertFalse(DataElement.objects.filter(uscdi_url__icontains="uscdi-v4"))
        self.assertFalse(DataElement.objects.filter(uscdi_url__icontains="healthit.gov/isa"))
        self.assertEqual(
            set(
                DataElement.objects.filter(data_element="Preferred Language").values_list(
                    "uscdi_url", flat=True
                )
            ),
            {"https://isp.healthit.gov/taxonomy/term/751/uscdi-v3-1"},
        )
        date_of_birth = DataElement.objects.get(data_element="Date of Birth")
        self.assertEqual(date_of_birth.mm_name, "Birth Date")
        self.assertEqual(
            date_of_birth.mm_elementId,
            "918225f5-4ffd-47a1-b7b1-27635f5429f6",
        )
        self.assertEqual(
            date_of_birth.mm_containingGuideId,
            "2d53584d-0853-4fa2-a153-0debce2ec183",
        )
        self.assertEqual(date_of_birth.hl7v2_identifier, "N/A: PID-7")
        self.assertEqual(date_of_birth.hl7v2_segment_type, "PID")
        self.assertEqual(date_of_birth.hl7v2_field_position, 7)
        self.assertEqual(date_of_birth.hl7v2_component_position, -1)
        self.assertEqual(date_of_birth.hl7v2_data_type, "TS")
        self.assertEqual(date_of_birth.mm_matchMethod, "alias")
        self.assertGreater(date_of_birth.mm_matchScore, 0.9)
        self.assertEqual(date_of_birth.mm_containingGuideName, "Generic v3.0 - full")
        date_of_death = DataElement.objects.get(data_element="Date of Death")
        self.assertEqual(date_of_death.mm_name, "Deceased Date")
        self.assertEqual(date_of_death.hl7v2_segment_type, "PID")
        self.assertEqual(date_of_death.hl7v2_field_position, 29)
        self.assertEqual(
            DataElement.objects.get(data_element="Race").hl7v2_field_position,
            10,
        )
        self.assertFalse(
            DataElement.objects.filter(
                data_element__in=(
                    "Encounter Diagnosis",
                    "Encounter Disposition",
                    "Encounter Location",
                    "Encounter Time",
                    "Encounter Type",
                )
            ).exclude(mm_name="")
        )
        self.assertIn("Collapsed 1 duplicate canonical row", stdout.getvalue())

    def test_missing_canonical_header_fails_before_database_writes(self):
        bad_path = self.write_csv(
            "bad.csv",
            [field for field in CANONICAL_FIELDS if field != "Applicable Standards"],
            [],
        )

        with self.assertRaisesMessage(CommandError, "Applicable Standards"):
            call_command(
                "loaduscdi31dataelements",
                uscdi_csv=bad_path,
                public_health_csv=self.public_health_path(),
                mmg_json=self.mmg_path(),
                stdout=StringIO(),
            )

        self.assertFalse(DataElement.objects.exists())
        self.assertFalse(DomainType.objects.filter(code="USCDI").exists())
        self.assertFalse(UseCaseType.objects.filter(code="USCDI-V3-1").exists())

    def test_invalid_mmg_json_fails_before_database_writes(self):
        bad_mmg = self.directory / "bad-mmg.json"
        bad_mmg.write_text("not JSON", encoding="utf-8")

        with self.assertRaisesMessage(CommandError, "Invalid MMG JSON"):
            call_command(
                "loaduscdi31dataelements",
                uscdi_csv=self.canonical_path(),
                public_health_csv=self.public_health_path(),
                mmg_json=bad_mmg,
                stdout=StringIO(),
            )

        self.assertFalse(DataElement.objects.exists())

    def test_invalid_source_with_replace_preserves_existing_rows(self):
        options = self.command_options()
        call_command("loaduscdi31dataelements", stdout=StringIO(), **options)
        existing_codes = set(DataElement.objects.values_list("code", flat=True))
        bad_mmg = self.directory / "bad-replacement-mmg.json"
        bad_mmg.write_text("not JSON", encoding="utf-8")

        with self.assertRaisesMessage(CommandError, "Invalid MMG JSON"):
            call_command(
                "loaduscdi31dataelements",
                replace=True,
                stdout=StringIO(),
                **{**options, "mmg_json": bad_mmg},
            )

        self.assertEqual(
            set(DataElement.objects.values_list("code", flat=True)),
            existing_codes,
        )


class DataElementViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="uscdi-viewer",
            password="test-password",
        )
        domain = DomainType.objects.create(code="USCDI", name="USCDI")
        data_class = DataClassType.objects.create(
            code="PATIENT-DEMOGRAPHICS",
            name="Patient Demographics/Information",
        )
        use_case = UseCaseType.objects.create(
            code="USCDI-V3-1",
            name="USCDI V3.1",
        )
        self.element = DataElement.objects.create(
            code="USCDI-V3-1-736",
            name="Date of Birth",
            description="The patient's date of birth.",
            domain=domain,
            data_class=data_class,
            use_case=use_case,
            classification_level="USCDI V3.1",
            data_element="Date of Birth",
            data_element_description="The patient's date of birth.",
            in_uscdi=True,
            uscdi_url=(
                "https://isp.healthit.gov/taxonomy/term/736/uscdi-v3-1"
            ),
            mm_name="Birth Date",
            mm_matchMethod="alias",
            mm_matchScore=0.925,
            mm_containingGuideName="Generic v3.0 - full",
            hl7v2_identifier="N/A: PID-7",
            hl7v2_segment_type="PID",
            hl7v2_field_position=7,
            hl7v2_component_position=-1,
            hl7v2_data_type="TS",
        )

    def test_as_json_contains_every_model_field_in_export_order(self):
        content = self.element.as_json

        self.assertEqual(tuple(content), DataElement.export_field_names())
        self.assertNotIn("id", content)
        self.assertNotIn("uscdi_uuid", content)
        self.assertEqual(content["data_element"], "Date of Birth")
        self.assertEqual(content["domain"], "USCDI")
        self.assertEqual(content["data_class"], "Patient Demographics/Information")
        self.assertEqual(content["mm_matchScore"], 0.925)
        self.assertIsInstance(content["created"], str)
        json.dumps(content)

    def test_export_exclusion_list_controls_headers_and_as_json(self):
        with patch.object(
            DataElement,
            "EXPORT_EXCLUDED_COLUMNS",
            ["id", "created", "updated"],
        ):
            content = self.element.as_json

            self.assertNotIn("id", DataElement.export_field_names())
            self.assertNotIn("created", DataElement.export_field_names())
            self.assertNotIn("updated", DataElement.export_field_names())
            self.assertNotIn("id", content)
            self.assertNotIn("created", content)
            self.assertNotIn("updated", content)

    def test_index_neatly_lists_data_and_both_download_actions(self):
        self.client.force_login(self.user)

        template = get_template("uscdi/index.html")
        template_source = template.template.source
        self.assertEqual(template_source.count("Download as CSV"), 2)
        self.assertEqual(template_source.count("Download as JSON"), 2)

        with patch(
            "apps.uscdi.views.render", return_value=HttpResponse("rendered")
        ) as render_mock:
            response = self.client.get(reverse("uscdi:uscdi_index"))

        self.assertEqual(response.status_code, 200)
        _, template_name, context = render_mock.call_args.args
        self.assertEqual(template_name, "uscdi/index.html")
        self.assertEqual(context["total_count"], 1)
        self.assertEqual(context["mapped_count"], 1)
        self.assertEqual(context["rows"][0]["element"], self.element)

    def test_index_starts_with_data_element_and_hl7v2_segment_columns(self):
        template = get_template("uscdi/index.html")
        content = template.render(
            {
                "rows": [
                    {
                        "element": self.element,
                        "ig_urls": [],
                        "us_core_urls": [],
                    }
                ],
                "total_count": 1,
                "mapped_count": 1,
                "unmapped_count": 0,
                "data_classes": [self.element.data_class.name],
            }
        )
        table_head = content.split("<thead>", 1)[1].split("</thead>", 1)[0]
        expected_headers = (
            "Data Element",
            "HL7v2 Segment",
            "Data Class",
            "Description and Standards",
            "HL7v2 Mapping",
            "References",
        )
        header_positions = [table_head.index(header) for header in expected_headers]
        self.assertEqual(header_positions, sorted(header_positions))

        first_row = content.split("<tbody>", 1)[1].split("</tr>", 1)[0]
        first_row_cells = first_row.split(">", 1)[1]
        self.assertLess(
            first_row_cells.index("Date of Birth"), first_row_cells.index("PID")
        )
        self.assertLess(
            first_row_cells.index("PID"),
            first_row_cells.index("Patient Demographics/Information"),
        )
        self.assertIn('colspan="6"', template.template.source)

    def test_csv_download_uses_complete_model_export(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("uscdi:export_to_csv"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertIn("uscdi-v3.1-data-elements-", response["Content-Disposition"])
        self.assertIn("no-cache", response["Cache-Control"])
        reader = csv.DictReader(StringIO(response.content.decode("utf-8-sig")))
        rows = list(reader)
        self.assertEqual(tuple(reader.fieldnames), DataElement.export_field_names())
        self.assertNotIn("id", reader.fieldnames)
        self.assertNotIn("uscdi_uuid", reader.fieldnames)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["data_element"], "Date of Birth")
        self.assertEqual(rows[0]["domain"], "USCDI")
        self.assertEqual(rows[0]["hl7v2_identifier"], "N/A: PID-7")

    def test_json_download_uses_complete_model_export(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("uscdi:export_to_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertIn("no-cache", response["Cache-Control"])
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertNotIn("id", payload["content"][0])
        self.assertNotIn("uscdi_uuid", payload["content"][0])
        self.assertEqual(payload["content"][0]["data_element"], "Date of Birth")
        self.assertEqual(payload["content"][0]["data_class"], "Patient Demographics/Information")
        self.assertEqual(payload["content"][0]["hl7v2_field_position"], 7)

    def test_views_require_authentication(self):
        for url_name in (
            "uscdi:uscdi_index",
            "uscdi:export_to_csv",
            "uscdi:export_to_json",
        ):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response.url)
