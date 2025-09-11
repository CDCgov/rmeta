
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from .get_phinvads import fetch, parse_valueset
from ...models import MDN
import csv
from io import StringIO
def flatten_valueset(valueset, common_name):
    results = []
    print(valueset)
    for c in valueset['codeset']:
        #print(json.dumps(c, indent=2))
        result = {'oid': valueset['id'], 
                  'common_name': common_name, 
                  'title': valueset['title'], 
                  'name': valueset['name'], 
                  'version': valueset['version']}
        result['code'] = c['code']
        result['code_display'] = c['display']
        result['code_system'] = c['system']
        result['code_version'] = c['version']
        results.append(result)
    return results
        
def reformat_fhir_valueset(fhir_valueset, host_prefix, fhir_prefix,
                           fhir_version,resource_version, contact,publisher):
    fhir_valueset['url'] = f"{host_prefix}/{fhir_prefix}/{fhir_version}/ValueSet/{fhir_valueset['id']}"
    fhir_valueset['version'] = resource_version
    fhir_valueset['contact'] = [{
        "telecom": [{
            "system": "email",
            "value": f"mailto:{contact}"}]}] 
    fhir_valueset['publisher'] = publisher
    if 'name' in fhir_valueset:
        fhir_valueset['name'] = fhir_valueset['name'].strip('PHVS_')
    return fhir_valueset
   
class Command(BaseCommand):
    help = "Get ValueSet from PHINVADS FHIR into the MDN database model"
    
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('host_prefix')
        parser.add_argument('--fhir_prefix', type=str, default='fhir',
                            help='Prefix for FHIR API endpoint')
        parser.add_argument('--fhir_version', type=str, default='R6', 
                            help='Version as part of URL of resource to use')
        parser.add_argument('--resource_version', type=str, default='1', 
                            help='Version of the FHIR API to use')
        parser.add_argument('--contact', type=str, default='aviars@cdc.gov', 
                            help='Contact email for FHIR resource')
        parser.add_argument('--publisher', type=str, default='CDC OPHDST - aviars@cdc.gov', 
                            help='Publisher information for FHIR resource')
    def handle(self, *args, **options):

       for mdn in MDN.objects.filter(data_element_type="coded"):
            print(f"Processing MDN: {mdn.common_name} ({mdn.oid})")
            if not mdn.oid:
                print(f"Skipping MDN {mdn.common_name} due to missing OID")
                continue
            else:
                oid = mdn.oid
                common_name = mdn.common_name
                # Fetch the FHIR valueset using the OID
                print(f"Fetching FHIR valueset for OID: {oid}")
                # Assuming fetch is a function that retrieves the FHIR valueset
                # from PHIN VADS using the OID
                fhir_valueset = fetch(mdn.oid)
                fhir_valueset= reformat_fhir_valueset(fhir_valueset, 
                                                      options['host_prefix'],
                                                      options['fhir_prefix'],
                                                      options['fhir_version'],
                                                      options['resource_version'],
                                                      options['contact'],
                                                      options['publisher'])
                
                
                mdn.fhir_body= json.dumps(fhir_valueset, indent=2)
                
                # Parse the valueset and flatten it
                parsed_valueset = parse_valueset(fhir_valueset, mdn.common_name)
                #flattened_valueset = flatten_valueset(parsed_valueset, mdn.common_name) 
                # Load the flattened valueset into the MDN model
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=parsed_valueset[0].keys())
                writer.writeheader()
                for i in parsed_valueset:
                    writer.writerow(i)
                
                mdn.csv_body = csv_buffer.getvalue()
                mdn.save()
               
        #self.stdout.write(
        #    self.style.NOTICE(f'Fetch {common_name} {oid} from PHIN VADS FHIR'))
        #load_data(oid, common_name)
        # fhir_valueset = fetch(oid)
        # parsed_valueset = parse_valueset(fhir_valueset, common_name)
        # load_flattened_valueset(parsed_valueset)
    
        #self.stdout.write(
        #    self.style.SUCCESS(f'Successfully loaded {oid} into OID data model'))

