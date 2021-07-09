from django_filters import rest_framework as filters
from apps.core.models import Inmueble, Municipio


class InmuebleFilter(filters.FilterSet):
    recamaras = filters.NumberFilter(field_name='recamaras', lookup_expr='gte')
    precio_min = filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = filters.NumberFilter(field_name='precio', lookup_expr='lte')
    estado = filters.NumberFilter(field_name='municipio__estado')
    full_text = filters.Filter(field_name='search_vector', lookup_expr='icontains')
    class Meta:
        model = Inmueble
        fields = ('titulo', 'descripcion', 'dueno', 'acepta_credito',
                  'categoria', 'tipo_propiedad', 'municipio', 'precio',
                  'moneda', 'precio_periodo', 'status', 'estacionamientos',
                  'banos', 'medios_banos', 'direccion',
                  'latitud', 'longitud', 'creada', 'actualizada',
                  'precio_min', 'precio_max', 'recamaras', 'full_text',
                  'acepta_mascotas')


class MunicipioFilter(filters.FilterSet):
    class Meta:
        model = Municipio
        fields = ('estado',)
