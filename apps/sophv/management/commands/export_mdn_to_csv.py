from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import MDN
import csv

def export_file(filename):
    mdns = MDN.objects.filter(pa=False)
    with open(filename, 'w', newline='') as csvfile:
        print(mdns[0].to_dict().keys())
        writer = csv.DictWriter(csvfile, fieldnames=mdns[0].to_dict().keys())
        writer.writeheader()
        for i in mdns:
            writer.writerow(i.to_dict())
    
   
class Command(BaseCommand):
    help = "Export MDN table to CSV"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('filename')

    def handle(self, *args, **options):
        export_file(options['filename'])
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported MDN table to CSV.'))

