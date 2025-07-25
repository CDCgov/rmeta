import requests
import json
import argparse

URL = "https://phinvads.cdc.gov/baseStu3/ValueSet/"



def fetch(oid): # Check if the response is already in the cache
   url = URL + oid
   response = requests.get(url)
   response.raise_for_status()  # Raise an exception for HTTP errors
   return response.json()

def parse_valueset(fhir_valuset, common_name=""):
    codesets = []
    if not common_name:
        common_name = fhir_valuset['name']
    parsed_valueset = {"common_name": common_name}
    
    for key in ['id', 'name', 'version', 'title']:
        if key in fhir_valuset:
            parsed_valueset[key] = fhir_valuset[key]

    if "compose" in fhir_valuset:
        if "include" in fhir_valuset["compose"]:
            for code in fhir_valuset["compose"]["include"]:
                for concept in code['concept']:
                    myset = parsed_valueset
                    myset["oid"]= fhir_valuset['id']
                    if '/' in concept['code']:
                        concept['code'] = concept['code'].replace('/','%2F')

                    myset['code'] = concept['code']
                    myset['code_system']= code['system']
                    myset['code_version'] = code['version']
                    myset['code_display'] = concept['display']
                    codesets.append(myset.copy())
    return codesets



# Fetch all pages and cache the responses
if __name__ == "__main__":
    # Parse args
    parser = argparse.ArgumentParser(description='Get valuesets from PHINVADS FHIR service. Print JSON output to stdout')
    parser.add_argument(
        dest='oid',
        action='store',
        help="OID of item to fetch")
    parser.add_argument(
        dest='common_name',
        action='store',
        help="A common name identifer used for the data element. For example, sex.")
    
    args = parser.parse_args()


    result = fetch(args.oid)
    print("Fetched", result['name'])
    parse_result = parse_valueset(result, args.common_name)
    
    print(json.dumps(parse_result, indent=4))





