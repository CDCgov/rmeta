"""Load code systems and their uses from codesystem-ref-list.json."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.uscdi.models import CodeReference, Uses


DEFAULT_SOURCE = Path(__file__).resolve().parents[2] / "codesystem-ref-list.json"
CODE_FIELDS = {
    "url", "version", "status", "name", "title", "description", "oids", "uses"
}


class Command(BaseCommand):
    help = "Import or refresh code references and their uses from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", nargs="?", type=Path, default=DEFAULT_SOURCE,
            help="Path to codesystem-ref-list.json (defaults to the bundled file).",
        )

    def handle(self, *args, **options):
        source = options["json_file"]
        try:
            records = json.loads(source.read_text(encoding="utf-8"))["codeSystems"]
        except (OSError, UnicodeError, ValueError, KeyError) as exc:
            raise CommandError(f"Could not read code references from {source}: {exc}") from exc

        if not isinstance(records, list):
            raise CommandError("codeSystems must be a list.")

        parsed = []
        seen_code_urls = set()
        use_names = {}
        for position, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise CommandError(f"Code system {position} must be an object.")
            oids = record.get("oids")
            if (
                not isinstance(oids, list) or len(oids) != 1
                or not isinstance(oids[0], str) or not oids[0]
            ):
                raise CommandError(
                    f"Code system {position} must have exactly one string OID."
                )

            code_url = record.get("url")
            if not isinstance(code_url, str) or not code_url:
                raise CommandError(f"Code system {position} has no URL.")
            if code_url in seen_code_urls:
                raise CommandError(f"Duplicate code system URL: {code_url}")
            seen_code_urls.add(code_url)

            nested_uses = record.get("uses", {})
            if not isinstance(nested_uses, dict):
                raise CommandError(f"Code system {position} has invalid uses.")
            # The supplied file has empty 'uses' objects. Its actual use URL
            # and name pairs are additional keys on each code system object.
            use_pairs = dict(nested_uses)
            for key, value in record.items():
                if key not in CODE_FIELDS:
                    use_pairs[key] = value
            for use_url, use_name in use_pairs.items():
                if (
                    not isinstance(use_url, str) or not use_url
                    or not isinstance(use_name, str) or not use_name
                ):
                    raise CommandError(f"Code system {position} has an invalid use.")
                if use_url in use_names and use_names[use_url] != use_name:
                    raise CommandError(f"Conflicting names for use URL: {use_url}")
                use_names[use_url] = use_name

            for key in ("name", "title", "status"):
                if not isinstance(record.get(key), str) or not record[key]:
                    raise CommandError(f"Code system {position} has no {key}.")
            parsed.append((record, oids[0], use_pairs))

        with transaction.atomic():
            use_objects = {
                url: Uses.objects.update_or_create(
                    url=url, defaults={"name": name}
                )[0]
                for url, name in use_names.items()
            }
            for record, oid, use_pairs in parsed:
                reference, _ = CodeReference.objects.update_or_create(
                    url=record["url"],
                    defaults={
                        "version": record.get("version"),
                        "status": record["status"],
                        "name": record["name"],
                        "title": record["title"],
                        "description": record.get("description") or "",
                        "oid": oid,
                    },
                )
                reference.uses.set(use_objects[url] for url in use_pairs)

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {len(parsed)} code references, {len(use_objects)} uses, "
                f"and {sum(len(use_pairs) for _, _, use_pairs in parsed)} links."
            )
        )

