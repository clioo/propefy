from rest_framework import (authentication, permissions, viewsets,
                            mixins)
from .serializers import (InmuebleSerializer, ImagenesSerializer,
                          TipoPropiedadSerializer, MunicipioSerializer,
                          EstadoSerializer, HistorialVisitasSerializer)
from apps.core.models import (Estado, Inmueble, Imagenes, Municipio,
                              TipoPropiedad, HistorialVisitas)
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from .filters import InmuebleFilter, MunicipioFilter
from apps.utils.utils import CreateListModelMixin
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from rest_framework.response import Response


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
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = InmuebleFilter
    serializer_class = InmuebleSerializer
    queryset = Inmueble.objects.all()

    def get_queryset(self):
        longitude = self.request.query_params.get('longitude', 0)
        latitude = self.request.query_params.get('latitude', 0)
        if self.request.query_params.get('longitude', 0) != 0:
            return super().get_queryset()
        user_location = Point(float(latitude), float(longitude), srid=4326)
        dataset = self.queryset.annotate(
            distance=Distance('point', user_location)
        ).order_by('distance')
        return dataset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user if not self.request.user.is_anonymous else None
        HistorialVisitas.objects.create(
            user=user,
            inmueble=instance
        )
        serializer = self.get_serializer(instance)
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
        return self.queryset.order_by('?')    


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
