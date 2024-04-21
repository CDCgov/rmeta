from django.core.management.base import BaseCommand
import csv
from ...models import DataClassType, DataElementType, DomainType, UseCaseType
import glob

def load_uscdi_types(input_csv_filename):
    rowindex = 0
    error_list = []
    created = []
    
    csvhandle = csv.DictReader(open(input_csv_filename, encoding='utf-8', errors='ignore'),  delimiter=',')
    for row in csvhandle:
        dt, g_o_c = DomainType.objects.get_or_create(uscdi_uuid=row["Domain"], name=row["Domain Name"])
        if g_o_c:
            created.append(dt.name)
        dct, g_o_c = DataClassType.objects.get_or_create(uscdi_uuid=row["Data Class"], name=row["Data Class Name"])
        if g_o_c:
            created.append(dct.name)
        uct, g_o_c = UseCaseType.objects.get_or_create(uscdi_uuid=row["Use Case"], name=row["Use Case Name"])
        if g_o_c:
            created.append(uct.name)
        rowindex +=1

    return {"rows": rowindex, "created": created, "total": len(created)}


class Command(BaseCommand):
    help = "Load USCDI Types from CSV."

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('input_csv_filename')
        ## Positional arguments
        #parser.add_argument('output_csv_filename')

    def handle(self, *args, **options):
        r = load_uscdi_types(options['input_csv_filename'])
        print(r)
