from apps.inmueble.providers import geo_provider
from django.contrib.gis.geos import Point
from apps.inmueble.lib.constants import GEO_SRID


def get_point_from_lat_lng(lat: float, lng: float) -> Point:
    return geo_provider.get_point_from_lat_lng(lat=lat, lng=lng)
