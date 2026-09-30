import csv
import difflib
import html
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from slugify import slugify

from ...models import DataClassType, DataElement, DomainType, UseCaseType


USCDI_VERSION = "USCDI V3.1"
USCDI_URL_TEMPLATE = (
    "https://isp.healthit.gov/taxonomy/term/{term_id}/uscdi-v3-1"
)

# The ISP CSV does not expose taxonomy IDs. These IDs were read from the
# corresponding USCDI V3.1 links on the official ISP data-class pages. Keeping
# them locally makes the import deterministic and usable without network access.
USCDI_V3_1_TERM_IDS = {
    "Assessment and Plan of Treatment": "581",
    "Author Organization": "801",
    "Author Time Stamp": "796",
    "BMI Percentile (2 - 20 years)": "876",
    "Body Height": "841",
    "Body Temperature": "861",
    "Body Weight": "846",
    "Care Team Member Identifier": "1291",
    "Care Team Member Location": "1296",
    "Care Team Member Name": "1286",
    "Care Team Member Role": "1301",
    "Care Team Member Telecom": "1316",
    "Clinical Test": "2456",
    "Clinical Test Result/Report": "3166",
    "Consultation Note": "601",
    "Coverage Status": "3601",
    "Coverage Type": "2351",
    "Current Address": "756",
    "Date of Birth": "736",
    "Date of Death": "2726",
    "Date of Diagnosis": "1241",
    "Date of Resolution": "1251",
    "Diagnostic Imaging Report": "2471",
    "Diagnostic Imaging Test": "2466",
    "Diastolic Blood Pressure": "831",
    "Disability Status": "3276",
    "Discharge Summary Note": "606",
    "Dose": "1236",
    "Dose Units of Measure": "1516",
    "Email Address": "921",
    "Encounter Diagnosis": "1201",
    "Encounter Disposition": "1196",
    "Encounter Location": "1336",
    "Encounter Time": "1191",
    "Encounter Type": "1186",
    "Ethnicity": "746",
    "Fill Status": "1586",
    "First Name": "706",
    "Functional Status": "3241",
    "Group Identifier": "2361",
    "Head Occipital-frontal Circumference Percentile (Birth - 36 Months)": "886",
    "Health Concerns": "656",
    "Heart Rate": "851",
    "History & Physical": "611",
    "Immunizations": "666",
    "Indication": "1546",
    "Inhaled Oxygen Concentration": "871",
    "Last Name": "711",
    "Medications": "691",
    "Member Identifier": "2751",
    "Mental/Cognitive Status": "1616",
    "Middle Name (Including middle initial)": "721",
    "Name Suffix": "726",
    "Occupation": "3381",
    "Occupation Industry": "3376",
    "Patient Goals": "646",
    "Payer Identifier": "2346",
    "Phone Number": "761",
    "Phone Number Type": "916",
    "Preferred Language": "751",
    "Pregnancy Status": "1651",
    "Previous Address": "911",
    "Previous Name": "716",
    "Problems": "771",
    "Procedure Note": "631",
    "Procedures": "781",
    "Progress Note": "636",
    "Pulse Oximetry": "866",
    "Race": "741",
    "Reaction": "906",
    "Reason for Referral": "2631",
    "Related Person's Name": "2696",
    "Related Person's Relationship": "2671",
    "Relationship to Subscriber": "3581",
    "Respiratory Rate": "856",
    "Result Status": "2441",
    "SDOH Assessment": "1801",
    "SDOH Goals": "1836",
    "SDOH Interventions": "1841",
    "SDOH Problems/Health Concerns": "1806",
    "Sex": "731",
    "Smoking Status": "811",
    "Specimen Type": "2491",
    "Subscriber Identifier": "2341",
    "Substance (Drug Class)": "901",
    "Substance (Medication)": "896",
    "Systolic Blood Pressure": "836",
    "Tests": "676",
    "Tribal Affiliation": "3691",
    "Unique Device Identifier(s) for a patient's implantable device(s)": "821",
    "Values/Results": "681",
    "Weight-for-length Percentile (Birth - 24 Months)": "881",
}

CANONICAL_HEADERS = {
    "Classification Level",
    "Data Class",
    "Data Class Description",
    "Data Element",
    "Data Element Description",
    "Applicable Standards",
}
PUBLIC_HEALTH_HEADERS = {
    "Data Element Name",
    "Data Class Name",
    "Description",
    "Additional Information",
    "Current USCDI Level",
    "USCDI URL",
    "Applicable Vocabulary Standard(s)",
    "Associated IG or Profile URL(s)",
    "Associated US Core Profile URL(s)",
}

PUBLIC_CLASS_ALIASES = {
    "care team member(s)": "care team members",
    "patient demographics": "patient demographics/information",
}

# These are deliberately narrow semantic aliases.  They cover concepts whose
# MMGAT label is meaningfully different from the canonical USCDI label; ordinary
# punctuation, word-order, and minor spelling differences are handled below.
MMG_NAME_ALIASES = {
    "body height": ("Height",),
    "body temperature": ("Highest Measured Temperature",),
    "body weight": ("Weight",),
    "coverage type": ("Insurance",),
    "date of birth": ("Birth Date",),
    "date of diagnosis": ("Clinical Diagnosis Date", "Diagnosis Date"),
    "date of death": ("Deceased Date", "Date of Death"),
    "date of resolution": ("Illness End Date",),
    "disability status": ("Disability Type",),
    "dose": ("Medication Dose",),
    "dose units of measure": ("Antibiotic Dose Units",),
    "ethnicity": ("Ethnic Group",),
    "first name": ("Subject's First Name",),
    "immunizations": ("Vaccine Type",),
    "last name": ("Subject's Last Name",),
    "medications": ("Medication Name", "Medication"),
    "occupation": ("Current Occupation Standardized", "Current Occupation"),
    "occupation industry": ("Current Industry Standardized", "Current Industry"),
    "race": ("Race Category",),
    "related person's relationship": ("Surrogate Relationship To Patient",),
    "systolic blood pressure": ("Lowest Systolic BP",),
    "tests": ("Test Performed",),
    "values/results": ("Test Result",),
}

MMG_FUZZY_THRESHOLD = 0.90
MMG_FUZZY_MARGIN = 0.10
MMG_NAME_STOP_WORDS = {"a", "an", "of", "s", "the"}

GUIDE_STATUS_RANK = {
    "final": 7,
    "approvals": 6,
    "peerreview": 5,
    "externalreview": 4,
    "useracceptancetesting": 3,
    "pilottesting": 2,
    "development": 1,
}


def _clean(value):
    if value is None:
        return ""
    value = html.unescape(str(value)).replace("\xa0", " ")
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in value.split("\n")).strip()


def _key(value):
    value = unicodedata.normalize("NFKC", _clean(value))
    return " ".join(value.split()).casefold()


def _class_key(value):
    value = _key(value)
    return PUBLIC_CLASS_ALIASES.get(value, value)


def _name_words(value):
    """Return comparison words while preserving the source value unchanged."""

    normalized = unicodedata.normalize("NFKC", _clean(value)).casefold()
    return tuple(
        word
        for word in re.findall(r"[a-z0-9]+", normalized)
        if word not in MMG_NAME_STOP_WORDS
    )


def _name_signature(value):
    return " ".join(sorted(_name_words(value)))


def _name_similarity(left, right):
    left_tokens = _name_words(left)
    right_tokens = _name_words(right)
    left_words = " ".join(left_tokens)
    right_words = " ".join(right_tokens)
    if not left_words or not right_words:
        return 0.0
    ordered_score = difflib.SequenceMatcher(None, left_words, right_words).ratio()
    signature_score = difflib.SequenceMatcher(
        None, _name_signature(left), _name_signature(right)
    ).ratio()
    left_set = set(left_tokens)
    right_set = set(right_tokens)
    token_score = len(left_set & right_set) / len(left_set | right_set)
    return 0.55 * signature_score + 0.30 * token_score + 0.15 * ordered_score


TERM_IDS_BY_KEY = {_key(name): term_id for name, term_id in USCDI_V3_1_TERM_IDS.items()}


def _read_csv(path, required_headers, label):
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise CommandError(f"Unable to open {label} file {path}: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing = sorted(required_headers - headers)
        if missing:
            raise CommandError(
                f"{label} file {path} is missing required column(s): "
                f"{', '.join(missing)}"
            )
        return list(reader)


def _canonical_rows(path):
    source_rows = _read_csv(path, CANONICAL_HEADERS, "USCDI V3.1 CSV")
    rows_by_key = {}
    duplicates = 0

    for row_number, source in enumerate(source_rows, start=2):
        row = {name: _clean(value) for name, value in source.items()}
        if _key(row["Classification Level"]) != _key(USCDI_VERSION):
            raise CommandError(
                f"{path}:{row_number} has classification "
                f"{row['Classification Level']!r}; expected {USCDI_VERSION!r}."
            )

        data_class = row["Data Class"]
        element = row["Data Element"]
        if not data_class or not element:
            raise CommandError(
                f"{path}:{row_number} must have both Data Class and Data Element."
            )

        term_id = TERM_IDS_BY_KEY.get(_key(element))
        if term_id is None:
            raise CommandError(
                f"No verified USCDI V3.1 taxonomy URL is configured for "
                f"{data_class!r} / {element!r}."
            )
        row["term_id"] = term_id

        identity = (_key(data_class), _key(element))
        existing = rows_by_key.get(identity)
        if existing is None:
            rows_by_key[identity] = row
            continue

        comparable_fields = (
            "Classification Level",
            "Data Class Description",
            "Data Element Description",
            "Applicable Standards",
            "term_id",
        )
        if any(existing[field] != row[field] for field in comparable_fields):
            raise CommandError(
                f"Conflicting duplicate USCDI rows for {data_class!r} / {element!r}."
            )
        duplicates += 1

    if not rows_by_key:
        raise CommandError(f"USCDI V3.1 CSV {path} contains no data rows.")

    return list(rows_by_key.values()), duplicates


def _public_health_index(path):
    rows = _read_csv(path, PUBLIC_HEALTH_HEADERS, "Public Health USCDI+ CSV")
    index = defaultdict(list)
    legacy_v4_rows = 0
    for row in rows:
        cleaned = {name: _clean(value) for name, value in row.items()}
        name = cleaned["Data Element Name"]
        if name:
            index[_key(name)].append(cleaned)
        if "uscdi v4" in _key(cleaned["Current USCDI Level"]):
            legacy_v4_rows += 1
    return index, legacy_v4_rows


def _matching_public_rows(canonical_row, public_index):
    canonical_class = _class_key(canonical_row["Data Class"])
    return [
        row
        for row in public_index.get(_key(canonical_row["Data Element"]), [])
        if _class_key(row["Data Class Name"]) == canonical_class
    ]


def _load_mmg_index(path):
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            payload = json.load(handle)
    except OSError as exc:
        raise CommandError(f"Unable to open MMG JSON file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CommandError(f"Invalid MMG JSON in {path}: {exc}") from exc

    guides = payload.get("result") if isinstance(payload, dict) else None
    if not isinstance(payload, dict) or payload.get("statusCode") != 200:
        raise CommandError(
            f"MMG JSON {path} must be an object with statusCode 200."
        )
    if not isinstance(guides, list):
        raise CommandError(f"MMG JSON {path} must contain a top-level result array.")

    index = defaultdict(list)
    source_order = 0
    for guide_number, guide in enumerate(guides, start=1):
        if not isinstance(guide, dict):
            raise CommandError(f"MMG guide #{guide_number} is not an object.")
        parent_guide_id = _clean(guide.get("id"))
        parent_guide_name = _clean(guide.get("name"))
        parent_guide_status = _clean(guide.get("guideStatus"))
        parent_guide_active = bool(guide.get("isActive"))
        blocks = guide.get("blocks") or []
        if not isinstance(blocks, list):
            raise CommandError(f"MMG guide {parent_guide_id!r} has a non-array blocks value.")

        for block in blocks:
            if not isinstance(block, dict):
                raise CommandError(f"MMG guide {parent_guide_id!r} contains an invalid block.")
            parent_block_id = _clean(block.get("id"))
            elements = block.get("elements") or []
            if not isinstance(elements, list):
                raise CommandError(
                    f"MMG block {parent_block_id!r} has a non-array elements value."
                )

            for element in elements:
                if not isinstance(element, dict):
                    raise CommandError(
                        f"MMG block {parent_block_id!r} contains an invalid element."
                    )
                name = _clean(element.get("name"))
                mappings = element.get("mappings") or {}
                hl7v251 = mappings.get("hl7v251") if isinstance(mappings, dict) else None
                if not name or not isinstance(hl7v251, dict):
                    continue

                occurrence = dict(element)
                occurrence["_hl7v251"] = hl7v251
                occurrence["_parent_guide_id"] = parent_guide_id
                occurrence["_parent_guide_name"] = parent_guide_name
                occurrence["_parent_guide_status"] = parent_guide_status
                occurrence["_parent_guide_active"] = parent_guide_active
                occurrence["_parent_block_id"] = parent_block_id
                occurrence["_source_order"] = source_order
                source_order += 1
                index[_key(name)].append(occurrence)
    return index


def _guide_name_is_stable(mapping):
    guide_name = _key(mapping.get("_parent_guide_name"))
    unstable_markers = (
        "copy",
        "csv",
        "developer",
        "do not use",
        "dontuse",
        "duplicate",
        "test",
    )
    return not any(marker in guide_name for marker in unstable_markers)


def _guide_quality(mapping):
    guide_status = re.sub(
        r"[^a-z]", "", _key(mapping.get("_parent_guide_status"))
    )
    preferred_guides = {
        "generic v3.0 - full": 3,
        "generic v3.0": 2,
        "case notification mdn": 1,
    }
    return (
        _guide_name_is_stable(mapping),
        _key(mapping.get("status")) == "final",
        bool(mapping.get("_parent_guide_active")),
        preferred_guides.get(_key(mapping.get("_parent_guide_name")), 0),
        GUIDE_STATUS_RANK.get(guide_status, 0),
        bool(_clean(mapping.get("_hl7v251", {}).get("identifier"))),
        _key(mapping.get("_parent_guide_id")),
        _key(mapping.get("id")),
        -_as_int(mapping.get("ordinal")),
    )


def _hl7_signature(mapping):
    hl7 = mapping["_hl7v251"]
    return (
        _key(hl7.get("segmentType")),
        _as_int(hl7.get("fieldPosition")),
        _as_int(hl7.get("componentPosition")),
    )


def _select_occurrence(mappings):
    """Choose one reproducible, representative occurrence for an MMG name."""

    usable_mappings = [
        mapping
        for mapping in mappings
        if _clean(mapping["_hl7v251"].get("segmentType"))
        and _as_int(mapping["_hl7v251"].get("fieldPosition")) > 0
    ]
    if usable_mappings:
        mappings = usable_mappings

    signature_counts = Counter(_hl7_signature(mapping) for mapping in mappings)
    best_signature = max(
        signature_counts,
        key=lambda signature: (
            signature_counts[signature],
            max(
                _guide_quality(mapping)
                for mapping in mappings
                if _hl7_signature(mapping) == signature
            ),
        ),
    )
    candidates = [
        mapping for mapping in mappings if _hl7_signature(mapping) == best_signature
    ]
    return max(candidates, key=_guide_quality)


def _select_mmg_mapping(element_name, mmg_index):
    """Resolve one conservative name match and one representative occurrence."""

    element_key = _key(element_name)
    aliases = MMG_NAME_ALIASES.get(element_key, ())
    for alias in aliases:
        candidates = mmg_index.get(_key(alias), [])
        if candidates:
            return (
                _select_occurrence(candidates),
                "alias",
                _name_similarity(element_name, alias),
                len(candidates),
            )

    exact_candidates = mmg_index.get(element_key, [])
    if exact_candidates:
        return _select_occurrence(exact_candidates), "exact", 1.0, len(exact_candidates)

    signature = _name_signature(element_name)
    signature_matches = [
        candidates
        for candidate_key, candidates in mmg_index.items()
        if _name_signature(candidate_key) == signature
    ]
    if len(signature_matches) == 1:
        candidates = signature_matches[0]
        return _select_occurrence(candidates), "normalized", 1.0, len(candidates)

    scores = sorted(
        (
            (_name_similarity(element_name, candidate_key), candidate_key)
            for candidate_key in mmg_index
        ),
        reverse=True,
    )
    if not scores or scores[0][0] < MMG_FUZZY_THRESHOLD:
        return None, "", 0.0, 0

    best_score, best_key = scores[0]
    runner_up_score = scores[1][0] if len(scores) > 1 else 0.0
    if best_score - runner_up_score < MMG_FUZZY_MARGIN:
        return None, "", 0.0, 0

    candidates = mmg_index[best_key]
    return _select_occurrence(candidates), "fuzzy", best_score, len(candidates)


def _merge_text(rows, field):
    values = []
    seen = set()
    for row in rows:
        value = _clean(row.get(field))
        if value and value not in seen:
            values.append(value)
            seen.add(value)
    return "\n\n".join(values)


def _updated_fhir_url(url, element_name):
    url = _clean(url)
    if not url:
        return ""

    url = re.sub(r"^http://(www\.)?hl7\.org/", "https://hl7.org/", url, flags=re.I)
    url = re.sub(r"^https://www\.hl7\.org/", "https://hl7.org/", url, flags=re.I)

    build_prefix = "https://build.fhir.org/ig/HL7/US-Core/"
    core_prefix = "https://hl7.org/fhir/us/core/"
    if url.startswith(build_prefix):
        suffix = url[len(build_prefix) :]
        url = f"{core_prefix}STU6.1/{suffix}"
    elif url.startswith(core_prefix):
        suffix = url[len(core_prefix) :]
        if not re.match(r"^(?:STU|[0-9])", suffix, flags=re.I):
            url = f"{core_prefix}STU6.1/{suffix}"

    ph_ballot_prefix = "https://hl7.org/fhir/us/ph-library/2022Sep/"
    if url.startswith(ph_ballot_prefix):
        suffix = url[len(ph_ballot_prefix) :]
        if (
            suffix == "StructureDefinition-us-ph-condition.html"
            and _key(element_name) == _key("Date of Diagnosis")
        ):
            suffix = "StructureDefinition-us-ph-condition-encounter-diagnosis.html"
        url = f"https://hl7.org/fhir/us/ph-library/STU2/{suffix}"

    return url


def _merge_urls(rows, field, element_name):
    values = []
    seen = set()
    for row in rows:
        for source_url in _clean(row.get(field)).split(","):
            url = _updated_fhir_url(source_url, element_name)
            if url and url not in seen:
                values.append(url)
                seen.add(url)
    return ",".join(values)


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return _clean(value).upper().startswith("Y") or _key(value) in {"1", "true"}


def _as_int(value):
    if value in (None, ""):
        return 0
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise CommandError(f"Expected an integer in MMG JSON, received {value!r}.") from exc


def _literal_values(value):
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return _clean(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _mapping_defaults(mapping, match_method="", match_score=None):
    if mapping is None:
        return {
            "mm_elementId": "",
            "mm_containingGuideId": "",
            "mm_containingGuideName": "",
            "mm_containingGuideStatus": "",
            "mm_containingBlockId": "",
            "mm_matchMethod": "",
            "mm_matchScore": None,
            "mm_guideId": "",
            "mm_guideInternalVersion": "",
            "mm_blockId": "",
            "mm_ordinal": 0,
            "mm_name": "",
            "mm_description": "",
            "mm_shortName": "",
            "mm_comments": "",
            "mm_status": "",
            "mm_dataType": "",
            "mm_businessRules": "",
            "mm_isUnitOfMeasure": False,
            "mm_codeSystem": "",
            "mm_legacyPriority": "",
            "mm_priority": "",
            "mm_isRepeat": False,
            "mm_mayRepeat": "",
            "mm_valueSetCode": "",
            "hl7v2_legacy_identifier": "",
            "hl7v2_identifier": "",
            "hl7v2_message_context": "",
            "hl7v2_data_type": "",
            "hl7v2_segment_type": "",
            "hl7v2_field_position": 0,
            "hl7v2_component_position": 0,
            "hl7v2_usage": "",
            "hl7v2_cardinality": "",
            "hl7v2_literalFieldValues": "",
            "hl7v2_repeatingGroupElementType": "",
            "hl7v2_sampleSegment": "",
        }

    hl7 = mapping["_hl7v251"]
    return {
        "mm_elementId": _clean(mapping.get("id")),
        "mm_containingGuideId": _clean(mapping.get("_parent_guide_id")),
        "mm_containingGuideName": _clean(mapping.get("_parent_guide_name")),
        "mm_containingGuideStatus": _clean(mapping.get("_parent_guide_status")),
        "mm_containingBlockId": _clean(mapping.get("_parent_block_id")),
        "mm_matchMethod": match_method,
        "mm_matchScore": match_score,
        "mm_guideId": _clean(mapping.get("guideId")),
        "mm_guideInternalVersion": _clean(mapping.get("guideInternalVersion")),
        "mm_blockId": _clean(mapping.get("blockId")),
        "mm_ordinal": _as_int(mapping.get("ordinal")),
        "mm_name": _clean(mapping.get("name")),
        "mm_description": _clean(mapping.get("description")),
        "mm_shortName": _clean(mapping.get("shortName")),
        "mm_comments": _clean(mapping.get("comments")),
        "mm_status": _clean(mapping.get("status")),
        "mm_dataType": _clean(mapping.get("dataType")),
        "mm_businessRules": _clean(mapping.get("businessRules")),
        "mm_isUnitOfMeasure": _as_bool(mapping.get("isUnitOfMeasure")),
        "mm_codeSystem": _clean(mapping.get("codeSystem")),
        "mm_legacyPriority": _clean(mapping.get("legacyPriority")),
        "mm_priority": _clean(mapping.get("priority")),
        "mm_isRepeat": _as_bool(mapping.get("isRepeat")),
        "mm_mayRepeat": _clean(mapping.get("mayRepeat")),
        "mm_valueSetCode": _clean(mapping.get("valueSetCode")),
        "hl7v2_legacy_identifier": _clean(hl7.get("legacyIdentifier")),
        "hl7v2_identifier": _clean(hl7.get("identifier")),
        "hl7v2_message_context": _clean(hl7.get("messageContext")),
        "hl7v2_data_type": _clean(hl7.get("dataType")),
        "hl7v2_segment_type": _clean(hl7.get("segmentType")),
        "hl7v2_field_position": _as_int(hl7.get("fieldPosition")),
        "hl7v2_component_position": _as_int(hl7.get("componentPosition")),
        "hl7v2_usage": _clean(hl7.get("usage")),
        "hl7v2_cardinality": _clean(hl7.get("cardinality")),
        "hl7v2_literalFieldValues": _literal_values(hl7.get("literalFieldValues")),
        "hl7v2_repeatingGroupElementType": _clean(
            hl7.get("repeatingGroupElementType")
        ),
        "hl7v2_sampleSegment": _clean(hl7.get("sampleSegment")),
    }


def _type_code(name):
    return str.upper(slugify(name.upper()))


def _data_class(row):
    code = _type_code(row["Data Class"])
    data_class, _ = DataClassType.objects.update_or_create(
        code=code,
        defaults={
            "name": row["Data Class"],
            "description": row["Data Class Description"],
        },
    )
    return data_class


def _element_code(term_id):
    return f"USCDI-V3-1-{term_id}"


class Command(BaseCommand):
    help = (
        "Load canonical USCDI V3.1 elements, Public Health FHIR enrichment, and "
        "one representative MMG/HL7v2 mapping into uscdi.DataElement. "
        "Exactly one row is maintained for each canonical USCDI element."
    )

    def add_arguments(self, parser):
        app_directory = Path(__file__).resolve().parents[2]
        parser.add_argument(
            "--uscdi-csv",
            type=Path,
            default=app_directory / "uscdi3.1-export-public.csv",
            help="Canonical USCDI V3.1 export CSV.",
        )
        parser.add_argument(
            "--public-health-csv",
            type=Path,
            default=app_directory / "PublicHealthUSCDI+2024-04-21.csv",
            help="Public Health USCDI+ CSV used only for FHIR enrichment.",
        )
        parser.add_argument(
            "--mmg-json",
            type=Path,
            default=app_directory / "MMGAT_Profiles.js",
            help="MMGAT profile JSON (the .js source is JSON data).",
        )
        parser.add_argument(
            "--no-prune",
            action="store_true",
            help=(
                "Retain stale rows in the command-owned USCDI-V3-1-* code "
                "namespace instead of reconciling them to the input files."
            ),
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help=(
                "Delete every existing uscdi.DataElement row inside the import "
                "transaction before loading the canonical V3.1 inventory."
            ),
        )

    def handle(self, *args, **options):
        if options["replace"] and options["no_prune"]:
            raise CommandError("--replace and --no-prune cannot be used together.")

        canonical_rows, duplicate_count = _canonical_rows(options["uscdi_csv"])
        public_index, legacy_v4_rows = _public_health_index(
            options["public_health_csv"]
        )
        mmg_index = _load_mmg_index(options["mmg_json"])

        created_count = 0
        updated_count = 0
        public_match_count = 0
        mmg_match_counts = Counter()
        mmg_candidate_count = 0
        pruned_count = 0
        replaced_count = 0
        desired_codes = set()

        with transaction.atomic():
            if options["replace"]:
                replaced_count = DataElement.objects.count()
                DataElement.objects.all().delete()

            domain, _ = DomainType.objects.update_or_create(
                code="USCDI",
                defaults={
                    "name": "USCDI",
                    "description": "United States Core Data for Interoperability",
                },
            )
            use_case, _ = UseCaseType.objects.update_or_create(
                code="USCDI-V3-1",
                defaults={
                    "name": USCDI_VERSION,
                    "description": "USCDI Version 3.1 (June 2025)",
                },
            )

            for row in canonical_rows:
                element_name = row["Data Element"]
                public_rows = _matching_public_rows(row, public_index)
                mapping, match_method, match_score, candidate_count = _select_mmg_mapping(
                    element_name, mmg_index
                )
                if public_rows:
                    public_match_count += 1
                if mapping is not None:
                    mmg_match_counts[match_method] += 1
                    mmg_candidate_count += candidate_count

                data_class = _data_class(row)
                fhir_ig_urls = _merge_urls(
                    public_rows,
                    "Associated IG or Profile URL(s)",
                    element_name,
                )
                fhir_core_urls = _merge_urls(
                    public_rows,
                    "Associated US Core Profile URL(s)",
                    element_name,
                )
                standards = row["Applicable Standards"]
                description = row["Data Element Description"] or _merge_text(
                    public_rows, "Description"
                )

                common_defaults = {
                    "name": element_name,
                    "description": description,
                    # The canonical export has no documented element UUID. The
                    # opaque Public Health identifier is intentionally not reused.
                    "uscdi_uuid": None,
                    "domain": domain,
                    "data_class": data_class,
                    "data_class_description": row["Data Class Description"],
                    "use_case": use_case,
                    "additional_information": _merge_text(
                        public_rows, "Additional Information"
                    ),
                    "in_uscdi": True,
                    "uscdi_url": USCDI_URL_TEMPLATE.format(term_id=row["term_id"]),
                    "applicable_vocabulary_standards": _merge_text(
                        public_rows, "Applicable Vocabulary Standard(s)"
                    ),
                    "classification_level": USCDI_VERSION,
                    "data_element": element_name,
                    "data_element_description": description,
                    "applicable_standards": standards,
                    "fhir_associated_ig_or_profile_urls": fhir_ig_urls,
                    "fhir_associated_us_core_profile_urls": fhir_core_urls,
                    "fhir_path": "",
                }

                defaults = {
                    **common_defaults,
                    **_mapping_defaults(mapping, match_method, match_score),
                }
                code = _element_code(row["term_id"])
                if code in desired_codes:
                    raise CommandError(
                        f"Multiple canonical USCDI elements resolve to code {code!r}."
                    )
                desired_codes.add(code)
                _, created = DataElement.objects.update_or_create(
                    code=code,
                    defaults=defaults,
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            if not options["no_prune"]:
                stale_rows = DataElement.objects.filter(
                    code__startswith="USCDI-V3-1-"
                ).exclude(code__in=desired_codes)
                pruned_count = stale_rows.count()
                stale_rows.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {len(canonical_rows)} canonical {USCDI_VERSION} elements "
                f"into {created_count + updated_count} rows "
                f"({created_count} created, {updated_count} updated)."
            )
        )
        match_summary = ", ".join(
            f"{count} {method}" for method, count in sorted(mmg_match_counts.items())
        ) or "none"
        self.stdout.write(
            f"Collapsed {duplicate_count} duplicate canonical row(s); "
            f"enriched {public_match_count} element(s) from Public Health USCDI+; "
            f"selected MMG mappings for {sum(mmg_match_counts.values())} element(s) "
            f"({match_summary}) from {mmg_candidate_count} candidate occurrence(s)."
        )
        self.stdout.write(
            f"Ignored legacy membership labels and URLs, including "
            f"{legacy_v4_rows} Public Health row(s) labeled USCDI V4."
        )
        if options["no_prune"]:
            self.stdout.write("Stale-row pruning was disabled with --no-prune.")
        else:
            self.stdout.write(
                f"Pruned {pruned_count} stale row(s) from the USCDI-V3-1-* "
                "code namespace."
            )
        if options["replace"]:
            self.stdout.write(
                f"Replacement mode removed {replaced_count} pre-existing "
                "DataElement row(s)."
            )

