"""Import the PHIG Excel metadata and its reviewed PIQI relationships."""

import posixpath
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.piqi_pcm.models import Attribute, ClinicalModel

from ...models import ReccomendedElement, SHEET_MODELS
from ...piqi_mappings import PIQI_MAPPING_NOTES, PIQI_MAPPINGS


DEFAULT_WORKBOOK = (
    Path(__file__).resolve().parents[2]
    / "PHIG B4 CCC and MCH Pilot Data Elements v3.xlsx"
)
XML_NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RELATIONSHIP_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
COLUMN_FIELDS = {
    "Use Case Data Element Name": "name",
    "USCDI v3.1 Element": "uscdi_element",
    "Rationale for Inclusion": "rationale_for_inclusion",
    "Base FHIR Profile": "base_fhir_profile",
    "Profile Data Element": "profile_data_element",
    "IG Must Support?": "ig_must_support",
    "IG Cardinality": "ig_cardinality",
    "IG Value Set, Other Value Set if Applicable": "ig_value_set",
    "Value Set Name": "value_set_name",
    "Value Set OID": "value_set_oid",
    "Code System(s) Name": "code_systems_name",
    "Notes": "notes",
}


def element_identifier(name):
    """Patient First Name -> PatientFirstName, independent of Excel row order."""
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "".join(word[0].upper() + word[1:] for word in re.findall(r"[A-Za-z0-9]+", normalized))


def worksheet_rows(archive, target, strings):
    """Read shared strings, inline strings and sparse cells without Excel packages."""
    root = ElementTree.fromstring(archive.read(target))
    for row in root.findall("x:sheetData/x:row", XML_NS):
        values = {}
        for cell in row.findall("x:c", XML_NS):
            value = cell.find("x:v", XML_NS)
            inline = cell.find("x:is", XML_NS)
            if cell.find("x:f", XML_NS) is not None and (value is None or value.text is None):
                raise CommandError(f"{target}: formula {cell.get('r')} has no cached value.")
            text = value.text or "" if value is not None else ""
            if cell.get("t") == "s":
                text = strings[int(text)]
            elif inline is not None:
                text = "".join(node.text or "" for node in inline.findall(".//x:t", XML_NS))
            elif cell.get("t") == "e":
                raise CommandError(f"{target}: cell {cell.get('r')} contains Excel error {text}.")
            if text.strip():
                column = re.sub(r"[0-9]", "", cell.get("r", ""))
                values[column] = text.strip()
        if values:
            yield int(row.get("r")), values


def read_workbook(source):
    """Validate every sheet before any records or relationships are written."""
    records = {}
    with ZipFile(source) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = [
                "".join(node.text or "" for node in item.findall(".//x:t", XML_NS))
                for item in ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            ]
        relationships = {
            item.get("Id"): item.get("Target")
            for item in ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        }
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        for sheet in workbook.findall("x:sheets/x:sheet", XML_NS):
            sheet_name = sheet.get("name")
            if sheet_name == "Reference":
                continue
            if sheet_name not in SHEET_MODELS:
                raise CommandError(f"Unsupported PHIG worksheet: {sheet_name!r}.")
            target = relationships[sheet.get(RELATIONSHIP_ID)]
            target = posixpath.normpath(
                target.lstrip("/") if target.startswith("/") else posixpath.join("xl", target)
            )
            rows = iter(worksheet_rows(archive, target, strings))
            header_row = next(rows, None)
            if header_row is None:
                raise CommandError(f"{sheet_name}: missing header row.")
            headers = {column: " ".join(value.split()) for column, value in header_row[1].items()}
            if set(headers.values()) != set(COLUMN_FIELDS) or len(headers) != len(COLUMN_FIELDS):
                raise CommandError(f"{sheet_name}: unexpected columns; expected {', '.join(COLUMN_FIELDS)}.")
            columns = {column: COLUMN_FIELDS[header] for column, header in headers.items()}
            records[sheet_name] = []
            section = ""
            seen = set()
            for row_number, cells in rows:
                if set(cells) - set(columns):
                    raise CommandError(f"{sheet_name} row {row_number}: data outside the header columns.")
                values = {field: cells.get(column, "") for column, field in columns.items()}
                name = values["name"]
                if not name:
                    raise CommandError(f"{sheet_name} row {row_number}: missing element name.")
                if all(not value for field, value in values.items() if field != "name"):
                    section = name
                    continue
                identifier = element_identifier(name)
                if not identifier or identifier in seen:
                    raise CommandError(f"{sheet_name} row {row_number}: duplicate or invalid identifier {identifier!r}.")
                seen.add(identifier)
                mnemonics = PIQI_MAPPINGS[sheet_name].get(identifier, ())
                values.update(
                    field_name=identifier, section=section, source_row=row_number,
                    piqi_mapping_notes=PIQI_MAPPING_NOTES.get(
                        (sheet_name, identifier),
                        "" if mnemonics else "No corresponding attribute in the selected PIQI clinical model.",
                    ),
                )
                try:
                    SHEET_MODELS[sheet_name](**values).full_clean(
                        validate_unique=False, validate_constraints=False,
                    )
                except ValidationError as exc:
                    raise CommandError(f"{sheet_name} row {row_number}: {exc}") from exc
                records[sheet_name].append((values, mnemonics))
        missing = set(SHEET_MODELS) - set(records)
        if missing:
            raise CommandError(f"Missing PHIG worksheets: {', '.join(sorted(missing))}.")
    return records


class Command(BaseCommand):
    help = "Refresh the six PHIG worksheets, master elements, and PIQI attribute links."

    def add_arguments(self, parser):
        parser.add_argument("--source", type=Path, default=DEFAULT_WORKBOOK)
        parser.add_argument("--piqi-model", default="PAT_CLINICAL_V1", help="PIQI clinical model mnemonic.")
        parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing.")

    def handle(self, *args, **options):
        try:
            records = read_workbook(options["source"])
        except (OSError, BadZipFile, ElementTree.ParseError, KeyError, ValueError, IndexError) as exc:
            raise CommandError(f"Could not read PHIG workbook: {exc}") from exc
        try:
            clinical_model = ClinicalModel.objects.get(mnemonic=options["piqi_model"])
        except ClinicalModel.DoesNotExist as exc:
            raise CommandError(
                f"PIQI model {options['piqi_model']!r} is not loaded. Run "
                "'python manage.py load_piqi_pcm' first or select --piqi-model."
            ) from exc

        required = {
            mnemonic for rows in records.values()
            for _, mnemonics in rows for mnemonic in mnemonics
        }
        attributes = defaultdict(list)
        for attribute in Attribute.objects.filter(
            data_class__clinical_model=clinical_model, mnemonic__in=required,
        ):
            attributes[attribute.mnemonic].append(attribute)
        invalid = sorted(mnemonic for mnemonic in required if len(attributes[mnemonic]) != 1)
        if invalid:
            raise CommandError(
                "Missing or ambiguous PIQI attributes in the selected model: "
                + ", ".join(invalid) + ". Refresh it with load_piqi_pcm before importing PHIG."
            )

        if not options["dry_run"]:
            with transaction.atomic():
                for sheet_name, rows in records.items():
                    for values, mnemonics in rows:
                        defaults = values.copy()
                        identifier = defaults.pop("field_name")
                        element, _ = SHEET_MODELS[sheet_name].objects.update_or_create(
                            field_name=identifier, defaults=defaults,
                        )
                        element.piqi_attributes.set(attributes[mnemonic][0] for mnemonic in mnemonics)
                        master, _ = ReccomendedElement.objects.update_or_create(
                            sheet_model=SHEET_MODELS[sheet_name].__name__,
                            field_name=identifier, defaults=defaults,
                        )
                        master.piqi_attributes.set(attributes[mnemonic][0] for mnemonic in mnemonics)

        total = linked = 0
        for sheet_name, rows in records.items():
            unmapped = [values["name"] for values, mnemonics in rows if not mnemonics]
            total += len(rows)
            linked += len(rows) - len(unmapped)
            self.stdout.write(f"{sheet_name}: {len(rows)} elements, {len(rows) - len(unmapped)} mapped.")
            if unmapped:
                self.stdout.write(self.style.WARNING("  Unmapped: " + "; ".join(unmapped)))
        action = "Would import" if options["dry_run"] else "Imported"
        self.stdout.write(self.style.SUCCESS(
            f"{action} {total} PHIG elements across {len(records)} worksheets; "
            f"{linked} have PIQI links, {total - linked} are unmapped."
        ))
