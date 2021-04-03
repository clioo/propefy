from django_filters import rest_framework as filters
from apps.core.models import Inmueble


class InmuebleFilter(filters.FilterSet):
    # tipo_inmueble
    # ciudad
    # estado
    # categoria
    # precio_min
    # precio_max
    # recamaras
    precio_min = filters.NumberFilter(field_name='price', lookup_expr='gt')
    class Meta:
        model = Inmueble
        fields = ('id', 'titulo', 'descripcion', 'dueno', 'acepta_credito',
                  'categoria', 'tipo_propiedad', 'municipio', 'precio',
                   'moneda', 'precio_periodo', 'status', 'estacionamientos',
                   'banos', 'medios_banos', 'direccion',
                   'latitud', 'longitud', 'creada', 'actualizada',
                   'precio_min')
