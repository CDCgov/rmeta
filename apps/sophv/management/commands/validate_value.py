import requests
import json
import argparse
import os
RESOLVER_URL = os.getenv("RESOLVER_URL", 'https://cdcmeta.com/sophv/api')
 
 
def validate_codeset_value(common_name, message_type, value): # Check if the response is already in the cache
   url = f'{RESOLVER_URL}/{common_name}/{message_type}/{value}'
   response = requests.get(url, verify=False, timeout=5)
   response.raise_for_status()  # Raise an exception for HTTP errors
   response_dict = response.json()
   return response_dict
 
 
if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description='Check a value against lookup table')
 
    parser.add_argument(
        dest='common_name',
        action='store',
        help="A common name identifer used for the data element. For example, sex.")
 
    parser.add_argument(
        dest='message_type',
        action='store',
        default='hl7v2',
        help="Must be 'csv', 'hl7v2', or 'fhir'.")
 
    parser.add_argument(
        dest='value',
        action='store',
        help="The coded value to check.")
 
    args = parser.parse_args()
    result = validate_codeset_value(args.common_name, args.message_type, args.value)
    print(json.dumps(result, indent=4))