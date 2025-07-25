
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from .get_phinvads import fetch, parse_valueset
from ...models import OID


def load_data(oid, common_name):
    fhir_valueset = fetch(oid)
    parsed_valueset = parse_valueset(fhir_valueset, common_name)
    load_flattened_valueset(parsed_valueset)

def flatten_valueset(valueset, common_name):
    results = []
    
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
        

def load_flattened_valueset(valueset):
    for vs in valueset:
        result = OID.objects.create(
            oid=vs['oid'],
            common_name=vs['common_name'],
            data_element_identifier_csv=vs['name'],
            name=vs['name'],
            title=vs['title'],
            version=vs['version'],
            code=vs['code'],
            fhir_code=vs['code'],
            fhir_code_display=vs['code_display'],
            code_display=vs['code_display'],
            code_system=vs['code_system'],
            code_system_version=vs['code_version'],
        )
        
   
class Command(BaseCommand):
    help = "Load a codeset from PHINVADS FHIR into the OID database model"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('oid')
        parser.add_argument('common_name')

    def handle(self, *args, **options):

        oid = options['oid']
        common_name = options['common_name']

        self.stdout.write(
            self.style.NOTICE(f'Fetch {common_name} {oid} from PHIN VADS FHIR'))
        load_data(oid, common_name)
        # fhir_valueset = fetch(oid)
        # parsed_valueset = parse_valueset(fhir_valueset, common_name)
        # load_flattened_valueset(parsed_valueset)
    
        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {oid} into OID data model'))

