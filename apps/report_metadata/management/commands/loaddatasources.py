from django.core.management.base import BaseCommand
import csv
from ...models import SourceSoftware, SourceSystem, HealthDataType, ProgramAreaType,Jurisdiction
from slugify import slugify
import glob

def get_jurisdictions():
    response= []
    for j in Jurisdiction.objects.all():
        response.append(j.code)
    return response

def get_program_area_type(filename):
    if "child" in filename.lower():
        return ProgramAreaType.objects.get(code="CHILD-LEAD")
    if "hiv" in filename.lower():
        return ProgramAreaType.objects.get(code="HIV")
    if "tuberculosis" in filename.lower():
        return ProgramAreaType.objects.get(code="TB")
    if "zoo" in filename.lower():
        return ProgramAreaType.objects.get(code="ZOO")
    if "syphilis" in filename.lower():
        return ProgramAreaType.objects.get(code="CS")
    if "std" in filename.lower():
        return ProgramAreaType.objects.get(code="STD")
    if "adult" in filename.lower():
        return ProgramAreaType.objects.get(code="ADULT-LEAD")
    if "flu" in filename.lower():
        return ProgramAreaType.objects.get(code="FLU")
    if "hepatitis" in filename.lower():
        return ProgramAreaType.objects.get(code="HEPATITIS")
    if "general" in filename.lower():
        return ProgramAreaType.objects.get(code="GENERAL-COMMUNICABLE")
    if "enteric" in filename.lower():
        return ProgramAreaType.objects.get(code="ENTERIC")
    if "vaccine" in filename.lower():
        return ProgramAreaType.objects.get(code="VACCINE-PREVENTABLE")


def load_datasources(input_csv_directory):
    myglob = "%s/*.csv" %(input_csv_directory)
    # print(glob.glob(myglob))
    jurisdictions = get_jurisdictions()
    rowindex = 0
    error_list = []
    total_software = 0
    total_systems = 0
    software_sources =[]
    software_systems =[]


    hl7v2 = HealthDataType.objects.get(code="HL7V2")
    other = HealthDataType.objects.get(code="OTHERFORMAT")
    mavenxml = HealthDataType.objects.get(code="MAVENXML")
    nbs_xml = HealthDataType.objects.get(code="NBSXML")
    flatfile = HealthDataType.objects.get(code="FLATFILE")
    sql = HealthDataType.objects.get(code="SQL")
    mycsv = HealthDataType.objects.get(code="CSV")
    cda = HealthDataType.objects.get(code="CDA")
    fhir = HealthDataType.objects.get(code="FHIR")



    for input_csv_filename in glob.glob(myglob):
        print("Processing", input_csv_filename)
        csvhandle = csv.reader(open(input_csv_filename, encoding='utf-8', errors='ignore'),  delimiter=',')
        for row in csvhandle:
            description =""
            if rowindex==0:
                header = row
            else:
                program_area = get_program_area_type(input_csv_filename)
                slug = str.upper(slugify(row[2].replace(" ", "").upper()))
                #print(program_area.code, program_area.id)
                if slug:
                    ss, g_or_c = SourceSoftware.objects.get_or_create(code=slug)
                    ss.name = row[2]
                    software_sources.append(ss.code)
                    ss.save()
                    #print(ss.name)
                    total_software +=1
                    software_sys_slug = "%s-%s" % (row[0],slug)
                    
                    software_sys, g_or_c = SourceSystem.objects.get_or_create(code = software_sys_slug,software=ss)
                    software_sys.program_areas.add(program_area)
                    if row[0] in jurisdictions:
                        jurisdiction = Jurisdiction.objects.get(code=row[0])
                        software_sys.jurisdiction = jurisdiction 
                    software_sys.name =row[1]
                    if "HL7" in row[4]:
                        software_sys.input_data_type = hl7v2
                    elif "MAVEN" in row[4]:
                        software_sys.input_data_type = hl7v2
                        software_sys.input_data_other_types.add(mavenxml)
                        
                    elif "NBS" in row[4]:
                        software_sys.output_data_type = hl7v2
                        software_sys.output_data_other_types.add(nbs_xml)

                    elif "Flat File" in row[4]:
                        software_sys.output_data_type = flatfile
                    elif "Other" in row[4]:
                        software_sys.output_data_type = other
                    elif "SQL" in row[4]:
                        software_sys.output_data_type = sql
                
                    elif "CSV" in row[4]:
                        software_sys.output_data_type = mycsv

                    elif "FHIR" in row[4]:
                        software_sys.output_data_type = fhir

                    elif "CDA" in row[4]:
                        software_sys.output_data_type = cda

                    if row[2] in ("Maven", "EpiTrax", "Sunquest", "NBS", "MAVEN"):
                        software_sys.output_data_type = hl7v2



                    software_sys.save()
                    software_systems.append(software_sys.code)

            rowindex+=1
        rowindex =0

    
    return {"total_software ":total_software, 
            "software_sources": set(software_sources),
            "software_systems": software_systems
            }


class Command(BaseCommand):
    help = "Load Data Sources"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('input_csv_directory')
        ## Positional arguments
        #parser.add_argument('output_csv_filename')

    def handle(self, *args, **options):
        r = load_datasources(options['input_csv_directory'])
        #print(r)
