import csv
from django.core.management.base import BaseCommand
from ...models import CDCDataElements, UseCaseType

class Command(BaseCommand):
    help = 'Load a CDC USCDI+ additions CSV into the database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.
            
            lde = UseCaseType.objects.get(name="Laboratory Data Exchange")
            cr = UseCaseType.objects.get(name="Case Reporting")
            for row in reader:
                
                if row[0]=='Laboratory Data Exchange':
                    use_case=lde
                elif row[0]=='Case Reporting':
                    use_case=cr

                _, created = CDCDataElements.objects.get_or_create(
                    UseCase=use_case,
                    Requester=row[1],
                    DataElementName=row[2],
                    Description=row[3],
                    In_USCDI=row[4],
                    If_Data_Element_Is_In_USCDI_What_Level_Is_It=row[5],
                    Remarks=row[6] if row[6] else None
                )