"""Reviewed PHIG-to-PIQI mappings, keyed by worksheet and element identifier.

Use exact mnemonics from the PIQI Patient Clinical Model, never fuzzy name
matches. Unlisted elements have no supported correspondence in that model.
Links to generic code/value attributes retain their clinical meaning in the
PHIG row's profile_data_element (including its LOINC/SNOMED qualifiers).
"""


PIQI_MAPPINGS = {
    "Foundational Dataset": {
        "PatientLastName": ("DEM_LASTNAME",),
        "PatientFirstName": ("DEM_FIRSTNAME",),
        "PatientAddress": ("DEM_CURRENTADDRESS",),
        "PatientDateOfBirth": ("DEM_DOB",),
        "Race": ("DEM_RACE",),
        "Ethnicity": ("DEM_ETHN",),
        "EncounterStatus": ("ENC_STATUS",),
        "EncounterClassification": ("ENC_ENCOUNTERCLASS",),
        "EncounterType": ("ENC_TYPE",),
        "EncounterDiagnosis": ("ENC_DIAGNOSIS",),
        "EncounterTime": ("ENC_STARTDATE", "ENC_ENDDATETIME"),
        "EncounterLocation": ("ENC_LOCATION",),
        "BloodPressurePanel": ("VIT_VITAL",),
        "SystolicBloodPressure": ("VIT_VITAL", "VIT_RESVAL", "VIT_RESUNIT"),
        "DiastolicBloodPressure": ("VIT_VITAL", "VIT_RESVAL", "VIT_RESUNIT"),
        "BodyHeight": ("VIT_VITAL", "VIT_RESVAL", "VIT_RESUNIT"),
        "BodyWeight": ("VIT_VITAL", "VIT_RESVAL", "VIT_RESUNIT"),
        "HeartRate": ("VIT_VITAL", "VIT_RESVAL", "VIT_RESUNIT"),
        "RespiratoryRate": ("VIT_VITAL", "VIT_RESVAL", "VIT_RESUNIT"),
        "ObservationStatus": ("VIT_RSTAT",),
        "VitalSignTypeCode": ("VIT_VITAL",),
        "ResultValueOrAbsentReasonConditional": (
            "VIT_RESVAL", "VIT_RESUNIT", "VIT_DATAABSENTREASON",
        ),
        "ComponentCodeAndValueConditional": (
            "VIT_VITAL", "VIT_RESVAL", "VIT_DATAABSENTREASON",
        ),
        "SpecimenCollectionTime": ("LAB_SPECCOLLDT",),
        "LabResultPerformer": ("LAB_PERFORMERNAME", "LAB_PERFORMERIDENTIFIER"),
        "ResultInterpretation": ("LAB_INT",),
        "ReferenceRange": ("LAB_REFRNG",),
        "TestNameTextAdditionalUSCDI": ("LAB_TEST",),
        "LabReportStatusRequired": ("LAB_RSTAT",),
        "LabReportCategoryRequired": ("LAB_CATEGORY",),
        "LabReportOrderCodeRequired": ("LAB_ORD",),
        "ReportEffectiveTimeConditional": ("LAB_PERFDT",),
        "ReportIssuedTimeConditional": ("LAB_RPTISSUEDT",),
        "ResponsibleLabPerformer": (
            "LAB_PERFSITE", "LAB_PERFORMERNAME", "LAB_PERFORMERIDENTIFIER",
        ),
    },
    "Foundational Must Support": {
        "PhoneNumber": ("DEM_TELECOM",),
        "PhoneNumberType": ("DEM_TELECOM",),
        "EmailAddress": ("DEM_EMAILADDRESS",),
        "TribalAffiliation": ("DEM_TRIBALAFFILIATION",),
        "DateOfDeath": ("DEM_DECDT",),
        "EncounterDisposition": ("ENC_DISPOSITION",),
        "MedicationCategory": ("MED_CATEGORY",),
        "DosageInstructionsSIG": ("MED_INSTR",),
        "ReasonIndicationAdditionalUSCDI": ("MED_IND",),
        "MedicationAdherenceAdditionalUSCDI": ("MED_ADHER",),
    },
    "Maternal Child Dataset": {
        "ImmunizationStatus": ("IMM_STATUS",),
        "VaccineProduct": ("IMM_VACC",),
        "AdministrationDate": ("IMM_ADMDT",),
    },
    "Maternal Child Must Support": {
        "LiveBirthVersusFetalDeathReportType": ("DOC_TYPE",),
        "BirthWeight": ("VIT_VITAL", "VIT_RESVAL", "VIT_RESUNIT"),
        "PrepregnancyDiabetes": ("CND_COND",),
        "GestationalDiabetes": ("CND_COND",),
        "PrepregnancyHypertension": ("CND_COND",),
        "GestationalHypertension": ("CND_COND",),
    },
    "Chronic Care Dataset": {
        "SDOHAssessmentScreeningQuestionAndResult": ("HA_ITEM", "HA_RESVAL"),
    },
    "Chronic Care Must Support": {},
}


PIQI_MAPPING_NOTES = {
    ("Foundational Dataset", "Sex"): (
        "No exact PIQI equivalent: the workbook's US Core sex extension is not "
        "the same concept as PIQI birthSex or genderIdentity."
    ),
    ("Foundational Dataset", "ComponentCodeAndValueConditional"): (
        "Partial mapping to vital sign code/value/absent reason. PIQI does not "
        "represent Observation.component grouping separately."
    ),
    ("Foundational Dataset", "SpecimenCollectionTime"): (
        "Mapped by the workbook's element name to specimenCollectionDateTime. "
        "The workbook lists Observation.effective[x]; confirm that the source "
        "actually represents specimen collection time."
    ),
    ("Foundational Dataset", "LabReportStatusRequired"): (
        "Partial mapping to lab resultStatus; PIQI has no separate "
        "DiagnosticReport status attribute."
    ),
    ("Foundational Dataset", "ReportEffectiveTimeConditional"): (
        "Partial mapping to lab performedDateTime; PIQI has no separate "
        "DiagnosticReport effective time attribute."
    ),
    ("Foundational Must Support", "PhoneNumberType"): (
        "Mapped to the telecom container; PIQI has no separate phone use/type attribute."
    ),
    ("Foundational Must Support", "DateWritten"): (
        "No exact PIQI equivalent for MedicationRequest.authoredOn; medication "
        "statementDate and startDate describe different events."
    ),
    ("Foundational Must Support", "QuantityDispensed"): (
        "No exact PIQI equivalent for dispensed quantity; doseQuantity describes "
        "the dose, not the amount dispensed."
    ),
    ("Chronic Care Dataset", "SDOHAssessmentScreeningQuestionAndResult"): (
        "Partial mapping to assessment and resultValue. PIQI Health Assessments "
        "has no dataAbsentReason attribute."
    ),
}
