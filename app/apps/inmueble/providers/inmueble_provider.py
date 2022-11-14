from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, GEOSGeometry
from django.db.models.query import QuerySet


def get_closest_inmuebles_by_point_ordered_by_distance(queryset: QuerySet, point: Point, radius_in_kms: int = None) -> QuerySet:
    queryset = queryset.annotate(
        distance=Distance('point', point)
    )
    if radius_in_kms:
        radius_in_meters = radius_in_kms * 1000
        queryset = queryset.filter(distance__lte=radius_in_meters)
    return queryset.order_by('distance')


def get_inmuebles_and_distance_from_point_in_polygon(queryset: QuerySet, point: Point, polygon: GEOSGeometry) -> QuerySet:
    return queryset.annotate(
                distance=Distance('point', point),
            ).order_by('distance').filter(point_geometry__intersects=polygon)
