from django.core.management.base import BaseCommand
import csv
from ...models import DataClassType, DataElementType, DomainType, UseCaseType
import glob

def load_uscdi_data_elements(input_csv_filename):
    rowindex = 0    
    csvhandle = csv.DictReader(open(input_csv_filename, encoding='utf-8', errors='ignore'),  delimiter=',')
    for row in csvhandle:
        dt = DomainType.objects.get(uscdi_uuid=row["Domain"], name=row["Domain Name"])
        dct = DataClassType.objects.get(uscdi_uuid=row["Data Class"], name=row["Data Class Name"])
        uct= UseCaseType.objects.get(uscdi_uuid=row["Use Case"], name=row["Use Case Name"])
        print(row["Data Element Name"])
        data_element, g_or_c = DataElementType.objects.get_or_create(name=row["Data Element Name"],
                                                    data_class=dct, domain=dt, use_case = uct)
        data_element.submission_status = row["Submission Status"]

        data_element.additional_information = row["Additional Information"]
        if row["In USCDI"] == "yes":
            data_element.in_uscdi = True
        data_element.current_uscdi_level = row["Current USCDI Level"]
        data_element.uscdi_url = row["USCDI URL"]
        data_element.uscdi_uuid = uscdi_uuid=row["Data Element"]
        data_element.description = row["Description"]
        data_element.applicable_vocabulary_standards =row["Applicable Vocabulary Standard(s)"]
        data_element.associated_reporting_program =row["Associated Reporting Program"]
        data_element.associated_reporting_program =row["Associated Reporting Program URL(s)"]
        data_element.associated_ig_or_profile =row["Associated IG or Profile"]
        data_element.associated_ig_or_profile_urls =row["Associated IG or Profile URL(s)"]	
        data_element.associated_us_core_profile= row["Associated US Core Profile"]
        data_element.associated_us_core_profile_urls =row["Associated US Core Profile URL(s)"]
        data_element.save()
        rowindex+=1


        

    
    return {"rows": rowindex}


class Command(BaseCommand):
    help = "Load USCDI Data Elements from CSV."

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('input_csv_filename')

    def handle(self, *args, **options):
        r = load_uscdi_data_elements(options['input_csv_filename'])
        print(r)
