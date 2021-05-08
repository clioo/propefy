import time
import csv
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from apps.core.models import Asentamiento, Municipio, Estado
import pandas as pd
from collections import defaultdict
from contextlib import suppress


class Command(BaseCommand):
    help = "This command imports to database a CSV containing Municipios, Estados, Colonias, etc..."

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)
    
    def get_numeric(cad:str, num_type=float):
        try:
            num = num_type(cad)
            return num
        except Exception:
            return None

    def formatted_postcode(self, postcode: str) -> str:
        postcode = str(postcode)
        while(len(postcode) < 5):
            postcode = '0' + postcode
        return postcode

    def handle(self, *args, **options):
        csv_file_path = options['csv_file'][0]
        data = pd.read_csv(csv_file_path, sep='|', encoding = "ISO-8859-1")
        # Loading localidades
        try:
            for i, row in data.iterrows():
                asentamiento = Asentamiento()
                asentamiento.codigo_postal = self.formatted_postcode(row.d_codigo)
                asentamiento.name = row.d_asenta
                asentamiento.tipo_asentamiento = row.d_tipo_asenta
                asentamiento.zona = row.d_zona
                asentamiento.ciudad = row.d_ciudad
                municipio = Municipio.objects.filter(estado__cve_entidad=row.c_estado, cve_municipio=row.c_mnpio)
                asentamiento.municipio = municipio.first()
                asentamiento.id_asenta_cp = row.id_asenta_cpcons
                with suppress(Exception):
                    asentamiento.save()
                
        except Exception as e:
            import pdb; pdb.set_trace()
            a = 1
