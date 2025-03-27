# Frontdoor


This software is designed to ingest and validate the following formats:

* HL7V2
* CCD
* FHIR
* CSV

Frontdoor is a Django app that provides an API and status URLS for data submission.. It relies on other built-in or 3rd party applications and libraries.  Most notably the "OAuth2 Provider" used here is the  is the library Django Oauth Toolkit. https://django-oauth-toolkit.readthedocs.io/en/latest/


This is a server-side reference implementation of the "CDC Submission Specification". The specification requires two files for propper submission.  These are the 

* `payload_file`
* `metadata_file`.  

The metadata file includes important information that can be missing or cannot be assertained from the payload itself.  This document describes the base REST API. 

SFTP, secure email, and other types of submission channels can be implemented around this API.

## Singleton Submission API Endpoint

The API allows you to a submit metadata and payload files to the server for processing.

### Endpoint URL
```
http://localhost:8000/frontdoor/api/submit/singleton
```

### HTTP Method
`POST`

### Headers
- `Authorization`: Bearer token is required for authentication. Replace `replace-w-your-oauth2-token` with your actual token.

### Request Parameters
- `metadata_field`: The metadata file to be uploaded. This should be a JSON file.
- `payload_field`: The payload file to be uploaded. This can be any supported file type.

### Example Request
Use the following `curl` command to call the API:

```bash
curl -F "metadata_field=@./sample-files/12345-sub-metadata.json" \
     -F "payload_field=@./sample-files/physical.ccda" \
     http://localhost:8000/frontdoor/api/submit/singleton \
     -H "Authorization: Bearer replace-w-your-oauth2-token"
```

Replace the placeholder values in the example with your actual file paths and authorization token.

### Response
The API will return a JSON response indicating the success or failure of the request. Ensure that the files and token are valid before making the request.

```json
{
    "status": "ACCEPTED",
    "transaction_control_number": "05f711ce-ac34-4e6c-be01-566dfa31cf47",
    "transaction_control_reference": "1234567892",
    "status_url": "http://localhost:8000/frontdoor/api/view/submission/1234567892",
    "submission": {
        "originating_agency_identifer": "DURHAM-NC-HEALTH-DEPT-01",
        "destination_agency_identifier": "1CDPMAIN",
        "submitter_agency_identifier": "APHL-01",
        "transaction_type": "SINGLETON",
        "contributing_agency_identifiers": [
            "NC-DEPT-HHS-01",
            "UNC-CH-01"
        ],
        "facility": "1437262961",
        "facility_postal_code": "27701",
        "subject_postal_code": "27707",
        "inbound_source_type": "REST-SUBMIT-API",
        "payload_type": "CCDA",
        "person_id_issuer": "UNK",
        "payload_hash": "297b467fda45c2e725ade5789b0ae9da7905c759",
        "date_created": "2025-03-27",
        "date_updated": "2025-03-27",
        "unique_payload": false
    },
    "warnings": [
        "Payload with identical hash 297b467fda45c2e725ade5789b0ae9da7905c759 has already been submitted.  This appears to be a duplicate.",
    ],
    "errors": []
}
```

Note the various parts of the submission response.  In the above example some `warnings` were returned but no `errors`.  When there are errors, the submission was not able to be processed, but messsages are acceppted with warnings.  Note that what is considdered an error or warning may differ depending on the type of data being submitted.  HL7V2x data must be parsable and begin with an `MSH` segment. FHIR data must be valid JSON Bundles, and CCD/CCDA (a.k.a. HL7V3) must be valid XML and valid against one or more profiles.  In this case a warning is displayed that an exact copy ogf this payload has has been seen before.
