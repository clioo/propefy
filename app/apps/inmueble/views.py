from rest_framework import (authentication, permissions, viewsets,
                            mixins)
from .serializers import (InmuebleSerializer, ImagenesSerializer,
                          TipoPropiedadSerializer, MunicipioSerializer,
                          EstadoSerializer)
from apps.core.models import (Estado, Inmueble, Imagenes, Municipio, TipoPropiedad)
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from .filters import InmuebleFilter, MunicipioFilter
from apps.utils.utils import CreateListModelMixin


class BaseInmuebleViewSet(viewsets.ModelViewSet):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class InmuebleViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = InmuebleFilter
    serializer_class = InmuebleSerializer
    queryset = Inmueble.objects.all()


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
