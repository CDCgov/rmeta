from django.core.management.base import BaseCommand
import csv
import sys
import json
import traceback
from collections import OrderedDict
from ...models import AnonyomizedDataNeed


def load_needs(input_csv_filename):
    csvhandle = csv.reader(open(input_csv_filename, encoding='utf-8', errors='ignore'),  delimiter=',')
    rowindex = 0
    error_list = []
    total = 0
    for row in csvhandle:
        description =""
        if rowindex==0:
            header = row
        else:
            print(rowindex, row[0])
            adn, g_or_c = AnonyomizedDataNeed.objects.get_or_create(
                eicr_data_element=row[0])
            
            if row[1]=="keep":               
                adn.keep = True
            elif row[1]!="":
                description="%s%s" % (description, row[1])
            
            if row[2]=="X":
                adn.hipaa_id = True
            elif row[2]!="":
                description="%s%s" % (description, row[2])

            if row[3]=="X":
                adn.in_syndromic_message = True
            elif row[3]!="":
                description="%s%s" % (description, row[3])
            
            adn.description=description
            adn.eicr_version= row[4]
            adn.eicr_template= row[6]
            adn.eicr_xpath = row[7]
            adn.save()
            total+=1
        rowindex+=1
    return {"total":total}


class Command(BaseCommand):
    help = "Load Annon Data Needs"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('input_csv_filename')
        ## Positional arguments
        #parser.add_argument('output_csv_filename')

    def handle(self, *args, **options):
        r = load_needs(options['input_csv_filename'])
        print(r)
