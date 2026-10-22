# PHIG Data Elements

The source is `PHIG B4 CCC and MCH Pilot Data Elements v3.xlsx` in this app.
Each of its six data worksheets has a concrete Django model and an admin:
`FoundationalDataset`, `FoundationalMustSupport`, `MaternalChildDataset`,
`MaternalChildMustSupport`, `ChronicCareDataset`, and `ChronicCareMustSupport`.
The `Reference` worksheet is excluded. Section headings become each element's
`section`; they are not imported as data elements. The v3 workbook has 91
elements; `Chronic Care Must Support` currently has only column headers.

## Master table

`ReccomendedElement` combines all six worksheets in one table and admin, shown
as **Recommended elements**. It includes every worksheet metadata field and the
PIQI attribute relationships. `sheet_model` uses `SHEET_MODEL_CHOICES`, storing
the original model name (for example `FoundationalDataset`) and displaying the
worksheet name. `(sheet_model, field_name)` is unique: the same field name in
different worksheets remains a separate row with its own metadata.

Migration `0002_reccomendedelement` copies all existing worksheet records and
their PIQI links into the master table. The original tables remain available.
Workbook imports refresh both the worksheet records and the master records.
Changes made directly to a worksheet record in admin do not automatically sync
to the master; edit the master when maintaining its recommendations.

The master supports optional many-to-many references to `uscdi.DataElement`,
`uscdi.MessageMappingGuide`, `uscdi.HL7Message`, `uscdi.HL7Segment`, and
`uscdi.CodeReference`, alongside the existing `piqi_pcm.Attribute` references.
These additional mappings are curated manually; imports do not infer them.
`uscdi_url` stores the USCDI reference, and `other_urls` accepts other reference
URLs, one per line. Each format has its own URL and multiline example fields:
`hl7v2_url` / `hl7v2_example`, `fhir_url` / `fhir_example`,
`cda_url` / `cda_example`, and `csv_url` / `csv_example`.

The master admin provides worksheet and section filters, search by metadata,
PIQI mnemonic and related references, and autocomplete for every relationship.
Workbook refreshes preserve the master's additional references, URLs, and examples.

## Import

From the project root, using the project's Python environment:

```powershell
python manage.py migrate
python manage.py load_piqi_pcm
python manage.py load_phig_data_elements --dry-run
python manage.py load_phig_data_elements
```

To load another copy of the workbook or select a PIQI clinical model:

```powershell
python manage.py load_phig_data_elements --source "path/to/workbook.xlsx" --piqi-model PAT_CLINICAL_V1
```

The command reads `.xlsx` directly using Python's standard library. It validates
all six worksheets, all twelve column headers, identifiers, and referenced PIQI
attributes before writing. Imports are atomic and can be rerun: the element's
`field_name` (for example `PatientFirstName`) is its unique key within a sheet,
so row reordering does not create duplicates. Spreadsheet metadata, source row,
and PIQI mappings are refreshed. Existing records absent from the workbook are
retained. Reimporting replaces any manually edited metadata and PIQI mappings
for elements present in the workbook. `--dry-run` validates without writing.

## PIQI relationships

`piqi_attributes` is a many-to-many relationship to `piqi_pcm.Attribute`, the
underlying table used by `DemographicsAttribute` and the other PIQI proxies.
It supports both single matches and composite rows such as encounter start/end
times. For example:

```python
from apps.phig_data_elements.models import FoundationalDataset

element = FoundationalDataset.objects.get(field_name="PatientFirstName")
attribute = element.piqi_attributes.get()
assert attribute.field_name == "firstName"
assert attribute.mnemonic == "DEM_FIRSTNAME"
```

All six admins display PIQI mnemonics as links to the corresponding attribute,
support searching by mnemonic, and allow editing relationships with autocomplete.

Mappings are explicit in `piqi_mappings.py` and scoped to the selected PIQI
clinical model (default `PAT_CLINICAL_V1`). Missing or ambiguous required
attributes stop the import with no writes. Unsupported concepts remain
unmapped and are listed in command output. `piqi_mapping_notes` explains partial
matches and known differences, including sex versus birth sex and report status
versus result status. A generic code/value attribute retains its clinical
qualifiers in the PHIG row's original `profile_data_element` text.

## Validation

```powershell
python manage.py test apps.phig_data_elements apps.piqi_pcm
python manage.py check
python manage.py makemigrations --check --dry-run phig_data_elements
```
