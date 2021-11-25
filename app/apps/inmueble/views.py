from rest_framework import (authentication, permissions, viewsets,
                            mixins)
from .serializers import (InmuebleSerializer, ImagenesSerializer,
                          TipoPropiedadSerializer, MunicipioSerializer,
                          EstadoSerializer, HistorialVisitasSerializer,
                          ProspectoVendedorSerializer,
                          ProspectoCompradorSerializer, AmenidadesSerializer)
from apps.core.models import (Estado, Inmueble, Imagenes, Municipio,
                              TipoPropiedad, HistorialVisitas,
                              ProspectoVendedor, ProspectoComprador,
                              HistorialBusquedas, Amenidades)
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from .filters import InmuebleFilter, MunicipioFilter
from apps.utils.utils import CreateListModelMixin
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance
from rest_framework.response import Response
from apps.utils.extra_fields import PatchModelMixin


def save_historial_busqueda(user, **kwargs):
    allowed_keys = {'recamaras', 'precio_min', 'precio_max', 'estado',
                    'full_text', 'titulo', 'descripcion', 'categoria',
                    'tipo_propiedad', 'latitude', 'longitude',}
    data = kwargs.copy()
    for key in kwargs.keys():
        value = kwargs[key][0]
        if key in {'latitude', 'longitude'}:
            data[key] = float(value)
        if key not in allowed_keys:
            data.pop(key)
    historialBusquedas = HistorialBusquedas(user=user, **data)
    historialBusquedas.save()


class BaseInmuebleViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          CreateListModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class InmuebleViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = InmuebleFilter
    serializer_class = InmuebleSerializer
    queryset = Inmueble.objects.all()

    def get_queryset(self):
        if len(self.request.query_params.keys()) > 2\
                and not self.request.user.is_anonymous:
            save_historial_busqueda(self.request.user,
                                    **self.request.query_params)
        longitude = self.request.query_params.get('longitude', 0)
        latitude = self.request.query_params.get('latitude', 0)
        polygon = self.request.query_params.get('polygon')
        distance = float(self.request.query_params.get('distance', 10)) * 1000
        if longitude == 0 and not polygon:
            return super().get_queryset()
        user_location = Point(float(longitude), float(latitude), srid=4326)
        if polygon:
            polygon = GEOSGeometry(polygon, 4326)
            dataset = self.queryset.annotate(
                distance=Distance('point', user_location),
            ).order_by('distance').filter(point_geometry__intersects=polygon)
        else:
            dataset = self.queryset.annotate(
                distance=Distance('point', user_location)
            ).order_by('distance').filter(distance__lte=distance)
        return dataset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user if not self.request.user.is_anonymous else None
        HistorialVisitas.objects.create(
            user=user,
            inmueble=instance
        )
        serializer = self.get_serializer(instance)
        serializer.instance.views_counter += 1
        serializer.instance.save()
        return Response(serializer.data)


class HistorialViewSet(BaseInmuebleViewSet):
    queryset = HistorialVisitas.objects.all()
    serializer_class = HistorialVisitasSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class RandomInmueblesViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin):
    serializer_class = InmuebleSerializer
    queryset = Inmueble.objects.all()

    def get_queryset(self):
        longitude = self.request.query_params.get('longitude', 0)
        latitude = self.request.query_params.get('latitude', 0)
        if longitude == 0:
            return super().get_queryset()
        user_location = Point(float(latitude), float(longitude), srid=4326)
        dataset = self.queryset.annotate(
            distance=Distance('point', user_location)
        ).order_by('distance')
        return dataset


class ImagenesInmuebleViewSet(viewsets.GenericViewSet,
                              mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              CreateListModelMixin):
    serializer_class = ImagenesSerializer
    queryset = Imagenes.objects.all()


class TipoInmuebleViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin):
    serializer_class = TipoPropiedadSerializer
    queryset = TipoPropiedad.objects.all()


class AmenidadesViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin):
    serializer_class = AmenidadesSerializer
    queryset = Amenidades.objects.all()


class EstadoViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin):
    serializer_class = EstadoSerializer
    queryset = Estado.objects.all()


class MunicipioViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MunicipioFilter
    serializer_class = MunicipioSerializer
    queryset = Municipio.objects.all()


class InmuebleLikeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                          PatchModelMixin):
    serializer_class = InmuebleSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Inmueble.objects.all()

    def partial_update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        # creating o removing like
        likes = instance.likes.filter(user=self.request.user)
        if likes:
            for like in likes:
                instance.likes.remove(like)
                like.delete()
        else:
            instance.likes.create(user=self.request.user)
        # ***
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_queryset(self):
        if self.action == 'partial_update':
            return self.queryset
        return self.queryset.filter(likes__user=self.request.user)


class ProspectoVendedorViewSet(BaseInmuebleViewSet):
    permission_classes = []
    queryset = ProspectoVendedor.objects.all()
    serializer_class = ProspectoVendedorSerializer

    def get_permissions(self):
        permissions_ = super().get_permissions()
        if self.action in ['list', 'retrieve', 'update', 'destroy']:
            permissions_ = (permissions.IsAuthenticated(),
                            permissions.IsAdminUser())
        return permissions_


class ProspectoCompradorViewSet(BaseInmuebleViewSet):
    permission_classes = []
    queryset = ProspectoComprador.objects.all()
    serializer_class = ProspectoCompradorSerializer

    def get_permissions(self):
        permissions_ = super().get_permissions()
        if self.action in ['list', 'retrieve', 'update', 'destroy']:
            permissions_ = (permissions.IsAuthenticated(),
                            permissions.IsAdminUser())
        return permissions_
