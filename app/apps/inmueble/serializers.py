from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.models import (Inmueble, Imagenes, TipoPropiedad, Municipio, Estado)
from apps.utils.extra_fields import HdBase64ImageField, ThumbnailBase64ImageField
from apps.user.serializers import UserSerializer
from apps.utils.extra_fields import RelatedFieldObjectRetriever
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ImagenesSerializer(serializers.ModelSerializer):
    photo = HdBase64ImageField(required=True)
    thumbnail = ThumbnailBase64ImageField(required=True)

    class Meta:
        model = Imagenes
        fields = ('id', 'inmueble', 'photo', 'thumbnail')


class InmuebleSerializer(serializers.ModelSerializer):
    imagenes_set = RelatedFieldObjectRetriever(
        required=False,
        queryset=Imagenes.objects.all(),
        serializer=ImagenesSerializer,
        many=True
    )

    class Meta:
        model = Inmueble
        fields = ('id', 'titulo', 'descripcion', 'dueno', 'acepta_credito',
                  'categoria', 'tipo_propiedad', 'municipio', 'precio',
                  'moneda', 'precio_periodo', 'status', 'estacionamientos',
                  'recamaras', 'banos', 'medios_banos', 'direccion',
                  'latitud', 'longitud', 'creada', 'actualizada',
                  'imagenes_set')
        extra_kwargs = {'id': {'read_only': True}}


class TipoPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPropiedad
        fields = ('id', 'nombre')
        extra_kwargs = {'id': {'read_only': True}}


class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = ('id', 'cve_municipio', 'nombre', 'estado')
        extra_kwargs = {'id': {'read_only': True}}

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ('id', 'nombre', 'cve_entidad', 'nombre_abreviacion')
