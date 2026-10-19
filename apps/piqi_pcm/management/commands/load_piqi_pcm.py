"""Load the supplied PIQI Patient Clinical Model metadata into Django."""

import json
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.piqi_pcm.models import Attribute, AttributeRole, ClinicalModel, DataClass


APP_DIR = Path(__file__).resolve().parents[2]
DEFAULT_JSON = APP_DIR / "Patient Clinical Model 1.0 - 08OCT2026.json"
DEFAULT_WORKBOOK = APP_DIR / "Patient Clinical Model 1.0 - 08OCT2026.xlsx"
XML_NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def workbook_icons(path):
    """Read the Data Classes worksheet's icon column without an Excel dependency."""
    if not path.exists():
        return {}

    with ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = [
                "".join(node.text or "" for node in item.findall(".//x:t", XML_NS))
                for item in root.findall("x:si", XML_NS)
            ]

        # The supplied workbook has its Data Classes sheet in the second slot.
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet2.xml"))
        icons = {}
        for row in sheet.findall("x:sheetData/x:row", XML_NS):
            values = {}
            for cell in row.findall("x:c", XML_NS):
                value = cell.find("x:v", XML_NS)
                inline = cell.find("x:is", XML_NS)
                if value is not None:
                    text = value.text or ""
                    if cell.get("t") == "s":
                        text = strings[int(text)]
                elif inline is not None:
                    text = "".join(
                        node.text or "" for node in inline.findall(".//x:t", XML_NS)
                    )
                else:
                    continue
                values["".join(c for c in cell.get("r", "") if c.isalpha())] = text
            if values.get("B") and values.get("G") and values["B"] != "Mnemonic":
                icons[values["B"]] = values["G"]
        return icons


class Command(BaseCommand):
    help = "Import or refresh the bundled PIQI Patient Clinical Model metadata."

    def add_arguments(self, parser):
        parser.add_argument("--source", type=Path, default=DEFAULT_JSON)
        parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)

    def handle(self, *args, **options):
        try:
            payload = json.loads(options["source"].read_text(encoding="utf-8"))
            icons = workbook_icons(options["workbook"])
        except (OSError, ValueError, KeyError) as exc:
            raise CommandError(f"Could not read PIQI source files: {exc}") from exc

        with transaction.atomic():
            clinical_model, _ = ClinicalModel.objects.update_or_create(
                mnemonic=payload["mnemonic"],
                defaults={
                    "name": payload["name"],
                    "description": payload.get("description") or "",
                    "version": payload["version"],
                    "model_type_name": payload["modelTypeName"],
                    "base_model": payload.get("baseModel") or "",
                    "root_entity_name": payload.get("rootEntityName") or "",
                    "root_entity_mnemonic": payload.get("rootEntityMnemonic") or "",
                },
            )
            class_count = attribute_count = role_count = 0
            for source_class in payload["dataClasses"]:
                cardinality = source_class.get("cardinality") or {}
                defaults = {
                    "name": source_class["name"],
                    "short_name": source_class.get("shortName") or "",
                    "field_name": source_class.get("fieldName") or "",
                    "description": source_class.get("description") or "",
                    "is_inherited": source_class.get("isInherited", False),
                    "sequence": source_class["sequence"],
                    "cardinality_name": cardinality.get("name") or "",
                    "cardinality_mnemonic": cardinality.get("mnemonic") or "",
                }
                if source_class["mnemonic"] in icons:
                    defaults["icon"] = icons[source_class["mnemonic"]]
                data_class, _ = DataClass.objects.update_or_create(
                    clinical_model=clinical_model,
                    mnemonic=source_class["mnemonic"],
                    defaults=defaults,
                )
                class_count += 1
                attributes = {}
                for source_attribute in source_class["attributes"]:
                    attribute_type = source_attribute.get("attributeType") or {}
                    attribute, _ = Attribute.objects.update_or_create(
                        data_class=data_class,
                        mnemonic=source_attribute["mnemonic"],
                        defaults={
                            "name": source_attribute["name"],
                            "short_name": source_attribute.get("shortName") or "",
                            "field_name": source_attribute.get("fieldName") or "",
                            "description": source_attribute.get("description") or "",
                            "sequence": source_attribute["sequence"],
                            "auto_generated": source_attribute.get("autoGenerated", False),
                            "is_inherited": source_attribute.get("isInherited", False),
                            "attribute_type_name": attribute_type["name"],
                            "attribute_type_mnemonic": attribute_type.get("mnemonic") or "",
                        },
                    )
                    attributes[attribute.mnemonic] = attribute
                    attribute_count += 1
                for source_role in source_class.get("roles", []):
                    try:
                        attribute = attributes[source_role["attributeMnemonic"]]
                    except KeyError as exc:
                        raise CommandError(
                            f"Role refers to unknown attribute {exc.args[0]} "
                            f"in {data_class.mnemonic}"
                        ) from exc
                    AttributeRole.objects.update_or_create(
                        attribute=attribute,
                        role_type_mnemonic=source_role["roleTypeMnemonic"],
                        defaults={"role_type_name": source_role["roleTypeName"]},
                    )
                    role_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {clinical_model}: {class_count} data classes, "
                f"{attribute_count} attributes, {role_count} roles."
            )
        )

