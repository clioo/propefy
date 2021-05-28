import time
import csv
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand
from apps.core.models import Municipio, Estado, Localidad, Asentamiento
from collections import defaultdict
from contextlib import suppress
from django.contrib.gis.gdal.datasource import DataSource
import os
import xml.etree.ElementTree as ET
from django.contrib.gis import geos


class Command(BaseCommand):
    help = "This command imports to database a CSV containing Municipios, Estados, Colonias, etc..."

    def handle(self, *args, **options):
        # Loading localidades
        try:
            base_path = '/polygons'
            gml_filename = ''
            for (dirpath, dirnames, filenames) in os.walk(base_path):
                for filename in filenames:
                    full_path = os.path.join(base_path, filename)
                    ds = DataSource(full_path)
                    geoms = ds[0].get_geoms(geos=True)
                    fields = ds[0].get_fields('d_cp')
                    data = zip(geoms, fields)
                    for polygon, cp in data:
                        if isinstance(polygon, geos.Polygon):
                            polygon = geos.MultiPolygon(polygon)
                        asentamientos = Asentamiento.objects.filter(codigo_postal=cp)
                        for asenta in asentamientos:
                            asenta.polygon = polygon
                            asenta.save()
            return gml_filename
                
        except Exception as e:
            import pdb; pdb.set_trace()
            a = 1
            pass
