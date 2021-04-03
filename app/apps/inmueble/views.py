from rest_framework import (authentication, permissions, viewsets,
                            mixins)
from .serializers import (InmuebleSerializer, ImagenesSerializer)
from apps.core.models import (Inmueble, Imagenes)
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from .filters import InmuebleFilter
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
