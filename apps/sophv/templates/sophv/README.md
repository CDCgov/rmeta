The Data Quality API can be used as a web service using any web server or CDN. It can also be downloaded to use directly or accessed via a RESTful webservice.

1. Working Locally or within your Environment
=============================================

To work locally, download and expand the following the latest CSV and JSON document download and expand the zip file:
[data-quality-latest.zip](https://dataquality.cdcmeta.com/data-quality-latest.zip)
The zip file contains data in both JSON and CSV formats. JSON is found in the `json` folder and CSV data is n the `csv` folder.

JSON
----

The JSON folder is a local replica of the JSON webservice described in the next section.  It contains over 200K files and is about 200MB in size.  Most of these files are comprised of single code set value files and their related metadata.

CSV
---

The `csv` folder contains the same data in the JSON format, but in only two files.  The file containing the data elements is `data_element.csv`. The file containing the code set values is `codeset_values.csv`.  The first row of each CSV file contains the field names.



2. Using the Web-based JSON API
===============================

Please the content of the JSON folder into a web server or CDN.  
The web server should be configured to serve the JSON files 
as static content.  The web server should also be configured to 
return `HTTP 404` for any file that does not exist. In the examples below,
the webserver is assumed to be running on `localhost` and the 
port is `80`, buy you may adjust this to your environment. Just replace
`localhost` with your web server's hostname or IP address add a port number 
if your webserver is not running on the default port `80`. For example, 
if your web server is running on `8080`, your URL would look like:

    [http://localhost:8080/age](http://localhost:8080/age)


At the top level, items are arranged by data element.  For each data element, it is accessed by its `common_name` like so.

 `http://[HOST]/[common_name]`


For example, to access `age`, your url may look like:


   [http://localhost/age](http://localhost/age)

This API call returns a JSON object with metadata about the data element.  Here is the `age` response body:


    {
        "data_element_name": "Age",
        "common_name": "age",
        "oid": "",
        "data_element_identifier_csv": "age",
        "data_element_description": "Person's age at time of calculated case counting date (CCCD)",
        "data_element_type": "numeric",
        "cdc_priority": "1",
        "may_repeat": "N",
        "value_set_name": "N/A",
        "value_set_code": "N/A",
        "csv_implementation_notes": "For unknown age, this data element may be left blank or populated with '9999'",
        "sample_value": "age: 32"
    }

The API returns metadata about the data element. Of chief interest is `data_element_type`, which is `numeric` and `data_element_name` which is `Age`.


Accessing Data Elements with a Code Sets and their Code Set APIs
--------------------------------------------------------------


Data elements with a `data_element_type` of `coded` contain a couple of extra values.  These are `static_json_hyperlink`, which contains a link to an HTML index of all possible code values. Use this to browse all possible coded values for a given data element. The field `static_json_api` shows how the API is to be called.  Let's take the coded data element `condition-code` as an example.

[http://localhost/condition-code.json](http://localhost/condition-code.json)

This call returns `HTTP 200` and the following JSON body.

	{
    "data_element_name": "Condition Code",
      "common_name": "condition-code",
      "oid": "2.16.840.1.114222.4.11.1015",
      "static_json_hyperlink": "http://localhost/2.16.840.1.114222.4.11.1015/index.html",
      "static_json_api": "http://localhost/2.16.840.1.114222.4.11.1015/[CODE].json",
      "data_element_identifier_csv": "condition_code",
      "data_element_description": "Condition or event that constitutes the reason the notification is being sent.",
      "data_element_type": "coded",
      "cdc_priority": "R",
      "may_repeat": "N",
      "value_set_name": "N/A",
      "value_set_code": "N/A",
      "csv_implementation_notes": "Refer to the National Notifiable Diseases Surveillance System Event Code List document for the relevant year.\r\n\r\nThis reference can be found on the NNDSS Technical Resource Center website under \"Event Codes and Other Surveillance Resources\" : https://ndc.services.cdc.gov/event-codes-other-surveillance-resources/",
      "sample_value": "condition_code: 11910"
	}

A given code can be checked by supplying a code to the API.  We will check the code `10056`.

 [http://localhost/2.16.840.1.114222.4.11.1015/10056.json](http://localhost/2.16.840.1.114222.4.11.1015/10056.json)

This call retuns an HTTP 200 and the following JSON body:

	{
      "pk": "2.16.840.1.114222.4.11.1015:10056",
      "oid": "2.16.840.1.114222.4.11.1015",
      "common_name": "condition-code",
      "name": "PHVS_NotifiableEvent_Disease_Condition_CDC_NNDSS",
      "title": "Nationally Notifiable Disease Surveillance System (NNDSS) & Other Conditions of Public Health Importance",
      "data_element_identifier_csv": "PHVS_NotifiableEvent_Disease_Condition_CDC_NNDSS",
      "version": "42",
      "code": "10056",
      "code_display": "West Nile virus disease, neuroinvasive",
      "code_system": "https://wwwn.cdc.gov/nndss/case-notification/related-documentation.html",
      "code_system_name": "",
      "code_system_version": "v42",
      "description": ""
	}

We can see the code `10056` is valid and represents `West Nile virus disease, neuroinvasive`.   Other metadata is also provided in the body's JSON response.

Errors
______

If you supply any invalid `common_name`, you will get a `404/Not` Found.  Any response that does not return `HTTP 200` with JSON content is and invalid request or data element common)name.
For example:

[http://localhost/aaagggee](http://localhost/aaagggee)

This API call returns an HTTP 404. Confifgure your webserver to reurn a custom 404 message body:

	{
    "code":404,
    "error":"Not Found"
    }

Provided the URL is otherwise correct, the "404/Not found" errors should means that the supplied code data element is invalid/incorrect/non-existent.

Similarly, using the codeset lookup API, if you supply an invalid code, you also get a 404 Not Found. Lets supply the non-existent code `1234` for considtion-code codeset lookup API.

[http://localhost/2.16.840.1.114222.4.11.1015/1234.json](http://localhost/2.16.840.1.114222.4.11.1015/1234.json)

This API returns the same HTTP 404 and the following message:

	{"code":404,"error":"Not Found"}
