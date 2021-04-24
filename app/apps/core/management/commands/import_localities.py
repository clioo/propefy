import time
import csv
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from apps.core.models import Municipio, Estado, Localidad
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

    def handle(self, *args, **options):
        estados_headers = {'Cve_Ent', 'Nom_Ent', 'Nom_Abr'}
        municipio_headers = {'Cve_Mun', 'Nom_Mun'}
        localidad_headers = {'Cve_Loc', 'Ámbito', 'Lat_Decimal',
            'Lon_Decimal', 'Pob_Total', 'Pob_Masculina', 'Pob_Femenina',
            'Total De Viviendas Habitadas'}
        allowed_headers = estados_headers.union(
            *municipio_headers).union(*localidad_headers)

        csv_file_path = options['csv_file'][0]
        data = pd.read_csv(csv_file_path)
        municipios = data.drop_duplicates(subset=["Cve_Ent", "Cve_Mun"])
        estados = data.drop_duplicates(subset=["Cve_Ent"])
        associations_est_mun = defaultdict(dict)
        # Loading Estados
        # with suppress(Exception):
        #     for i, j in estados.iterrows():
        #         estado = Estado()
        #         estado.nombre = j['Nom_Ent']
        #         estado.cve_entidad = j['Cve_Ent']
        #         estado.nombre_abreviacion = j['Nom_Abr']
        #         estado.save()
        # estados = Estado.objects.all()

        # Loading municipios
        with suppress(Exception):
            for i, j in municipios.iterrows():
                municipio = Municipio()
                municipio.nombre = j['Nom_Mun']
                municipio.cve_municipio = j['Cve_Mun']
                estado = estados.filter(cve_entidad=j['Cve_Ent']).first()
                municipio.estado = estado
                municipio.save()

        municipios = Municipio.objects.all()
        # Loading localidades
        try:
            for i, j in data.iterrows():
                localidad = Localidad()
                municipio = municipios.filter(cve_municipio=j['Cve_Mun'],
                                                estado__cve_entidad=j["Cve_Ent"]).first()
                localidad.municipio = municipio
                localidad.nombre = j['Nom_Loc']
                localidad.cve_localidad = j['Cve_Loc']
                localidad.ambito = j['�mbito']
                pob_total = self.get_numeric(j['Pob_Total'])
                localidad.pob_total = pob_total
                pob_masculina = self.get_numeric(j['Pob_Masculina'])
                localidad.pob_masculina = pob_masculina
                pob_femenina = self.get_numeric(j['Pob_Femenina'])
                localidad.pob_femenina = pob_femenina
                total_viviendas_habitadas = self.get_numeric(j['Total De Viviendas Habitadas'])
                localidad.total_viviendas_habitadas = total_viviendas_habitadas
                latitude = self.get_numeric(j['Lat_Decimal'])
                localidad.latitude = latitude
                longitude = self.get_numeric(j['Lon_Decimal'])
                localidad.longitude = longitude
                localidad.save()
        except Exception as e:
            import pdb; pdb.set_trace()
            a = 1
