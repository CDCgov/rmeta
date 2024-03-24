from django.core.management.base import BaseCommand
import csv
from ...models import Jurisdiction,Partner


def load_jurisdictions(input_csv_filename):
    csvhandle = csv.reader(open(input_csv_filename, encoding='utf-8', errors='ignore'),  delimiter=',')
    rowindex = 0
    error_list = []
    total = 0
    for row in csvhandle:
        description =""
        if rowindex==0:
            header = row
        else:
            jdn, g_or_c = Jurisdiction.objects.get_or_create(
                code=row[0])
            jdn.save()
            partner,g_or_c = Partner.objects.get_or_create(code=jdn.code, jurisdiction=jdn, name=jdn.name,
                                                           state_level=jdn.state_level)
            partner.state = jdn.state
            partner.save()
            total+=1
        rowindex+=1
    return {"total":total}


class Command(BaseCommand):
    help = "Load Jurisdictions"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('input_csv_filename')
        ## Positional arguments
        #parser.add_argument('output_csv_filename')

    def handle(self, *args, **options):
        r = load_jurisdictions(options['input_csv_filename'])
        print(r)
