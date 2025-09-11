from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import OID
import csv


def export_file(filename):
    oids = OID.objects.all()
    with open(filename, 'w', newline='') as csvfile:
        
        writer = csv.DictWriter(csvfile, fieldnames=oids[0].keys())
        writer.writeheader()
        for i in oids:
            writer.writerow(i.to_dict())
    
   
class Command(BaseCommand):
    help = "Export OID table to CSV"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('filename')

    def handle(self, *args, **options):
        export_file(options['filename'])
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported OID Table to CSV.'))

