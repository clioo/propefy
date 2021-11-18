from django_filters import rest_framework as filters
from apps.core.models import Inmueble, Municipio
from apps.utils.extra_fields import ListFilter


class InmuebleFilter(filters.FilterSet):
    recamaras_max = filters.NumberFilter(field_name='recamaras',
        lookup_expr='gte')
    recamaras_min = filters.NumberFilter(field_name='recamaras',
        lookup_expr='lte')
    precio_min = filters.NumberFilter(field_name='precio', lookup_expr='gte')
    precio_max = filters.NumberFilter(field_name='precio', lookup_expr='lte')
    estado = filters.NumberFilter(field_name='municipio__estado')
    full_text = filters.Filter(field_name='search_vector', lookup_expr='icontains')
    tipo_propiedad = ListFilter(field_name='tipo_propiedad_id')
    class Meta:
        model = Inmueble
        fields = ('titulo', 'descripcion', 'dueno', 'acepta_credito',
                  'categoria', 'tipo_propiedad', 'municipio', 'precio',
                  'moneda', 'precio_periodo', 'status', 'estacionamientos',
                  'banos', 'medios_banos', 'direccion',
                  'latitud', 'longitud', 'creada', 'actualizada',
                  'precio_min', 'precio_max', 'recamaras', 'full_text',
                  'dentro_de_privada', 'se_admiten_mascotas', 'amueblada')


class MunicipioFilter(filters.FilterSet):
    class Meta:
        model = Municipio
        fields = ('estado',)
