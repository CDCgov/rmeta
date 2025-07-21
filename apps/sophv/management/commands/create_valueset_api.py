from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import OID
import json
from django.template.loader import render_to_string
import os

def export_oid_json(directory_name, common_name,host_prefix=""):
    oids = OID.objects.filter(common_name=common_name)
    filename_index = []
    oid = oids[0].oid if oids else None
    title = oids[0].title if oids else None
    code_system_version = oids[0].code_system_version if oids else None
    code_system = oids[0].code_system if oids else None
    for o in oids:
        os.makedirs(f"{directory_name}/{o.oid}", exist_ok=True)
        filename = f"{directory_name}/{o.oid}/{o.code}.json"
        oid = o.oid
        filename_index.append(filename)
        with open(filename, 'w') as jsonfile:
            json.dump(o.to_dict(), jsonfile, indent=4)

    context = {'oids': oids, "oid": oid, 
                'common_name': common_name,
                'title': title,
                'code_system_version': code_system_version,
                'code_system': code_system,
                'directory_name': directory_name,
                'filename_index': filename_index,
                'host_prefix': host_prefix,
                }
    rendered_template = render_to_string('sophv/codeset-cdn.html', context)
    if oid:
        with open(f"{directory_name}/{oid}/index.html", 'w') as index_file:
            index_file.write(rendered_template)

   
class Command(BaseCommand):
    help = "Export Data element API as static JSON files"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('directory_name')
        parser.add_argument('common_name')

    def handle(self, *args, **options):
        export_oid_json(options['directory_name'], options['common_name'])
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported Codesets to to JSON.'))

