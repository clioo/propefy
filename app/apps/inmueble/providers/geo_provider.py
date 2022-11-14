from django.contrib.gis.geos import Point, GEOSGeometry
from apps.inmueble.lib.constants import GEO_SRID


def get_point_from_lat_lng(lat: float, lng: float) -> Point:
    return Point(float(lng), float(lat), srid=GEO_SRID)


def get_polygon_from_string(polygon: str) -> GEOSGeometry:
    return GEOSGeometry(polygon, GEO_SRID)
