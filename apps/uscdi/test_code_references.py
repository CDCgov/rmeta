import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib import admin
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from .models import CodeReference, Uses


class LoadCodeReferencesTests(TestCase):
    def test_import_populates_related_uses_and_is_idempotent(self):
        output = StringIO()
        call_command("load_code_references", stdout=output)
        call_command("load_code_references", stdout=output)

        self.assertEqual(CodeReference.objects.count(), 19)
        self.assertEqual(Uses.objects.count(), 36)
        self.assertEqual(
            sum(ref.uses.count() for ref in CodeReference.objects.all()), 44
        )
        loinc = CodeReference.objects.get(name="LOINC")
        self.assertEqual(loinc.oid, "2.16.840.1.113883.6.1")
        self.assertIsInstance(loinc.oid, str)
        self.assertEqual(loinc.uses.count(), 8)
        self.assertIsNone(CodeReference.objects.get(name="SNOMED_CT").version)

        shared_use = Uses.objects.get(url="ValueSet-valueset-sdtc-example.html")
        self.assertEqual(shared_use.code_references.count(), 2)
        self.assertTrue(admin.site.is_registered(CodeReference))
        self.assertTrue(admin.site.is_registered(Uses))

    def test_rejects_multiple_oids_without_writing(self):
        with TemporaryDirectory() as directory:
            source = Path(directory) / "invalid.json"
            source.write_text(
                json.dumps({
                    "codeSystems": [{
                        "url": "https://example.org/codes",
                        "name": "Example",
                        "title": "Example",
                        "status": "active",
                        "oids": ["1.2", "1.3"],
                        "uses": {},
                    }]
                }),
                encoding="utf-8",
            )
            with self.assertRaisesMessage(CommandError, "exactly one string OID"):
                call_command("load_code_references", source, stdout=StringIO())

        self.assertFalse(CodeReference.objects.exists())
        self.assertFalse(Uses.objects.exists())

