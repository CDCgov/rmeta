
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import DataElement

        

def get_valueset(oid, common_name=""):
    # TODO Write code to get valuset data from 1CDP
    # requests.get(1CDP_URL)....
    valueset = []
    
    for vs in valueset:
        if not common_name:
            common_name = vs['name']
        result = DataElement.objects.create(
            oid=vs['oid'],
            common_name=vs['common_name'],
            data_element_identifier_csv=common_name,
            name=vs['name'],
            version=vs['version'],
            code=vs['code'],
            fhir_code=vs['code'],
            fhir_code_display=vs['code_display'],
            code_display=vs['code_display'],
            code_system=vs['code_system'],
            code_system_version=vs['code_version'],
        )
        
   
class Command(BaseCommand):
    help = "Load a codeset from 1CDP into the DataElement DB model"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('oid')
        parser.add_argument('common_name')

    def handle(self, *args, **options):

        oid = options['oid']
        common_name = options['common_name']
        get_valueset(oid, common_name)
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded data from 1CDP into DataElement model'))

