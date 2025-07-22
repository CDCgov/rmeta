from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import MDN, OID
import json
import os
from django.template.loader import render_to_string
from .get_phinvads import fetch, parse_valueset
from .load_phinvads_to_oid import load_data
from .create_mdn_cdn import export_mdn_json
from .create_valueset_api import export_oid_json

def build_cdn(directory_name, host_prefix="", download=False):
    export_mdn_json(directory_name, host_prefix)
    print("Exported MDN JSON files to", directory_name)


    # Now lets go back through ang get all the coded oids.
    coded_data_elements = MDN.objects.filter(data_element_type="coded")

    for c in coded_data_elements:
        # Fetch the valueset from PHIN VADS
        if download:
         print(f'Fetching {c.common_name} {c.oid} from PHIN VADS FHIR and loading into reltinal database.')
         load_data(c.oid, c.common_name)
        # Now export the data element to JSON files
        export_oid_json(directory_name, c.common_name, host_prefix=host_prefix)





   
class Command(BaseCommand):
    help = "Export MDN table to as JSON files"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('directory_name')
        parser.add_argument('host_prefix')
        parser.add_argument('-d', '--download', action='store_true', help='EDownload files from phinvads')

    def handle(self, *args, **options):
        build_cdn(options['directory_name'], options['host_prefix'], options['download'])
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported Data Quality API to JSON.'))

