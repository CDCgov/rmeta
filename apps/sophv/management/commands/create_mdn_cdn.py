from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import MDN
import json
import os
from django.template.loader import render_to_string


def export_mdn_json(directory_name, host_prefix=""):
    mdns = MDN.objects.all().order_by('common_name')
    for m in mdns:
        #print(f"Exporting {m.common_name} to JSON")
        m.static_json_hyperlink = f"{host_prefix}/{m.oid}/index.html"
        m.static_json_api = f"{host_prefix}/{m.oid}/[CODE].json"
        m.save()
        os.makedirs(f"{directory_name}/", exist_ok=True)
        filename = f"{directory_name}/{m.common_name}.json"
        with open(filename, 'w') as jsonfile:
            json.dump(m.to_dict(), jsonfile, indent=4)
        #if it is of dat_element_type "coded"
        if m.data_element_type == "coded" and m.fhir_body:
            # write the FHIR JSON body to a file
            os.makedirs(f"{directory_name}/fhir/R6/Valueset", exist_ok=True) 
            with open(f"{directory_name}/fhir/R6/Valueset/{m.oid}", 'w') as vs_file:
                vs_file.write(m.fhir_body)
            # write the CSV body to a file
            os.makedirs(f"{directory_name}/csv", exist_ok=True)
            with open(f"{directory_name}/csv/{m.oid}.csv", 'w') as csv_file:
                csv_file.write(m.csv_body) 

    context = {'mdns': mdns, 'host_prefix': host_prefix,}
    rendered_template = render_to_string('sophv/mdn-cdn.html', context)
    with open(f"{directory_name}/index.html", 'w') as index_file:
        index_file.write(rendered_template)

   
class Command(BaseCommand):
    help = "Export MDN table as JSON files"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('directory_name')
        parser.add_argument('host_prefix')

    def handle(self, *args, **options):
        export_mdn_json(options['directory_name'], options['host_prefix'])
         # Create the directory if it doesn't exist
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created MDN static API.'))

