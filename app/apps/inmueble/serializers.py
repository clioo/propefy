from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.core.models import (Inmueble, Imagenes, TipoPropiedad, Municipio,
                              Estado, HistorialVisitas, ProspectoComprador,
                              ProspectoVendedor, Amenidades)
from apps.utils.extra_fields import HdBase64ImageField, ThumbnailBase64ImageField
from apps.user.serializers import UserSerializer
from apps.utils.extra_fields import RelatedFieldObjectRetriever
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from math import sin, cos, sqrt, atan2, radians


def calculate_distance(lat1_: float, lon1_: float, lat2_: float, lon2_: float):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = radians(lat1_)
    lon1 = radians(lon1_)
    lat2 = radians(lat2_)
    lon2 = radians(lon2_)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    # returns distance in KM
    return distance


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
    distance = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Inmueble
        fields = ('id', 'titulo', 'descripcion', 'dueno', 'acepta_credito',
                  'categoria', 'tipo_propiedad', 'municipio', 'precio',
                  'moneda', 'precio_periodo', 'status', 'estacionamientos',
                  'recamaras', 'banos', 'medios_banos', 'direccion',
                  'latitud', 'longitud', 'creada', 'actualizada',
                  'imagenes_set', 'distance', 'is_liked', 'destacado',
                  'antiguedad', 'views_counter', 'm_2', 'm_2_construccion',
                  'se_admiten_mascotas', 'amueblada', "amenidades")
        extra_kwargs = {'id': {'read_only': True}}

    def get_distance(self, instance):
        try:
            distance = instance.distance.m
        except:
            distance = 'Distance not available'
        return distance
    #     user_lat = self.context['request'].query_params.get('latitude', 0)
    #     user_lon = self.context['request'].query_params.get('longitude', 0)
    #     if user_lat == 0:
    #         return "Distancia no disponible."
    #     return calculate_distance(instance.latitud, instance.longitud,
    #                               float(user_lat), float(user_lon))

    def get_is_liked(self, instance):
        if not self.context['request'].user.is_anonymous:
            return instance.likes.filter(
                user_id=self.context['request'].user.id).exists()
        return (_('Not authenticated.'))


class HistorialVisitasSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialVisitas
        fields = ('id', 'user', 'inmueble', 'created')



class TipoPropiedadSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoPropiedad
        fields = ('id', 'nombre')
        extra_kwargs = {'id': {'read_only': True}}


class AmenidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenidades
        fields = ('id', 'name')
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


class ProspectoVendedorSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    class Meta:
        model = ProspectoVendedor
        fields = ('id', 'interested_phone_number', 'nombre', 'correo',
                  'inmueble', 'created', 'updated', 'is_active')
        extra_kwargs = {'id': {'read_only': True}}


class ProspectoCompradorSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    class Meta:
        model = ProspectoComprador
        fields = ('id', 'interested_phone_number', 'nombre', 'correo',
                  'inmueble' ,'created', 'updated', 'is_active')
        extra_kwargs = {'id': {'read_only': True}}
