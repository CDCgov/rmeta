
import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import MDN
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = "Generate an index page for FHIR ValueSets stored in the MDN database model"

    
    def add_arguments(self, parser):
         # Positional arguments

         parser.add_argument('--prefix', type=str, default='',
                             help='Prefix to add to the links.')
         parser.add_argument('--output', type=str, default='FHIRValueSets-output.html', help='Output file path for the generated index page.')
    
    def handle(self, *args, **options):
        count=0
        links_to_fhir_valuesets = []
        coded_mdns = MDN.objects.filter(data_element_type="coded")
        for mdn in coded_mdns:
            count += 1
            print(f"Processing MDN: {mdn.common_name} ({mdn.oid}) ({count})")
            link = f'{options["prefix"]}{mdn.oid}'
            #print(f"mdn.fhir_body: {mdn.fhir_body[:120]}")
            links_to_fhir_valuesets.append(link)
            # print(f"Link to FHIR ValueSet: {link}")

        context = {'mdns': coded_mdns, 'prefix': options['prefix'], 'links': links_to_fhir_valuesets}
        rendered_template = render_to_string('sophv/FHIRValueSets.html', context)
        template_path = os.path.join(settings.BASE_DIR, 'apps', 'sophv', 'templates', 'sophv', 'FHIRValueSets.html')
        output_path = options['output']
        with open(output_path, 'w') as index_file:
            index_file.write(rendered_template)

