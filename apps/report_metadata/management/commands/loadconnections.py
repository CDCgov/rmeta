from django.core.management.base import BaseCommand
from ...models import SourceSystem, HealthDataType, CDCReceivingSystem, Connection, Partner
from slugify import slugify
import csv
from django.db import models

def load_connections(input_csv_filename):
    csvhandle = csv.reader(open(input_csv_filename, encoding='utf-8', errors='ignore'),  delimiter=',')
    rowindex = 0
    nndss = CDCReceivingSystem.objects.get(code="NNDSS")
    total =0
    for row in csvhandle:
        if rowindex==0:
            header = row
        else:
            if row[1]:
                software_sys_slug = str.upper(slugify("%s-%s" % (row[0],row[1])))
                try:
                    #print(software_sys_slug)
                    source_system = SourceSystem.objects.get(code=software_sys_slug)
                    partner = Partner.objects.get(code=row[0])
                    connection, g_or_c = Connection.objects.get_or_create(partner=partner, 
                                            source_system=source_system, cdc_receiving_system=nndss)
                    total+=1
                except SourceSystem.DoesNotExist:
                    print("skiped",software_sys_slug)
        rowindex+=1
    return {"total":total}
            


class Command(BaseCommand):
    help = "Load Connections"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('input_csv_filename')


    def handle(self, *args, **options):
        r = load_connections(options['input_csv_filename'])
        print(r)
