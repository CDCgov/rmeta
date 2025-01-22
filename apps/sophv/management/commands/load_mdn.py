import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from ...models import MDN

class Command(BaseCommand):
    help = 'Load data from main.csv into MDN model'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'mdn2025.csv')
        
        with open(file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                phinvads_fhir_hyperlink = ""
                static_csv_hyperlink = ""
                if row['oid']:
                    phinvads_fhir_hyperlink = "https://phinvads.cdc.gov/baseStu3/ValueSet/%s" % (row['oid'])
                    static_csv_hyperlink = "http://static.cdcmeta.com/phinvads/latest/oid/%s.csv" % (row['oid'])
                print(row)
                MDN.objects.create(
                    data_element_name = row['data_element_name'],
                    data_element_identifier_csv = row['data_element_identifier_csv'],
                    common_name = row['data_element_identifier_csv'].replace("_", "-").replace("[n]","").lower(),
                    data_element_description = row['data_element_description'],
                    data_element_type = row['data_element_type'].lower(),
                    cdc_priority = row['cdc_priority'],
                    may_repeat = row['may_repeat'],
                    value_set_name = row['value_set_name'],
                    oid = row['oid'],
                    phinvads_fhir_hyperlink = phinvads_fhir_hyperlink ,
                    phinvads_hyperlink = row['phinvads_hyperlink'],
                    static_csv_hyperlink = static_csv_hyperlink,
                    value_set_code = row['value_set_code'],
                    csv_implementation_notes = row['csv_implementation_notes'],
                    sample_value = row['sample_value']

                )
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded CSV into MDN model'))

