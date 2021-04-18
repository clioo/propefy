import time
import csv
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from apps.core.models import Municipio, Estado, Localidad


class Command(BaseCommand):
    help = "This command imports to database a CSV containing Municipios, Estados, Colonias, etc..."

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file'][0]
        estados_headers = {'Cve_Ent', 'Nom_Ent', 'Nom_Abr'}
        municipio_headers = {'Cve_Mun', 'Nom_Mun'}
        localidad_headers = {'Cve_Loc', 'Ámbito', 'Lat_Decimal',
            'Lon_Decimal', 'Pob_Total', 'Pob_Masculina', 'Pob_Femenina',
            'Total De Viviendas Habitadas'}
        allowed_headers = estados_headers.union(
            *municipio_headers).union(*localidad_headers)
        												
        with open(csv_file_path, encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                import pdb; pdb.set_trace()
                if line_count == 0:
                    print(f'Column names are {", ".join(row)}')
                    line_count += 1
                else:
                    # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                    line_count += 1
            print(f'Processed {line_count} lines.')
