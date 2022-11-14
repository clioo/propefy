from rest_framework import serializers
from apps.core.models import (Inmueble, Imagenes, TipoPropiedad, Municipio,
                              Estado, HistorialVisitas, ProspectoComprador,
                              ProspectoVendedor, Amenidades)
from apps.utils.extra_fields import HdBase64ImageField, ThumbnailBase64ImageField
from apps.utils.extra_fields import RelatedFieldObjectRetriever
from django.utils.translation import gettext_lazy as _
from apps.inmueble.providers import inmueble_provider


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
        except AttributeError:
            distance = 'Distance not available'
        return distance

    def get_is_liked(self, instance):
        if not self.context['request'].user.is_anonymous:
            return instance.likes.filter(
                user_id=self.context['request'].user.id).exists()
        return (_('Not authenticated.'))


class SingleInmuebleSerializer(InmuebleSerializer):
    inmuebles_of_interest = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Inmueble
        fields = ('id', 'titulo', 'descripcion', 'dueno', 'acepta_credito',
                  'categoria', 'tipo_propiedad', 'municipio', 'precio',
                  'moneda', 'precio_periodo', 'status', 'estacionamientos',
                  'recamaras', 'banos', 'medios_banos', 'direccion',
                  'latitud', 'longitud', 'creada', 'actualizada',
                  'imagenes_set', 'distance', 'is_liked', 'destacado',
                  'antiguedad', 'views_counter', 'm_2', 'm_2_construccion',
                  'se_admiten_mascotas', 'amueblada', "amenidades",
                  "inmuebles_of_interest")
        extra_kwargs = {'id': {'read_only': True}}

    def get_inmuebles_of_interest(self, instance):
        if not instance.latitud or not instance.longitud:
            return []
        point = instance.point
        inmuebles = inmueble_provider.get_closest_inmuebles_by_point_ordered_by_distance(
            queryset=Inmueble.objects.all(),
            point=point
        ).exclude(id=instance.id)[:3]
        return [inmueble.id for inmueble in inmuebles]

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
                  'created', 'updated', 'is_active')
        extra_kwargs = {'id': {'read_only': True}}


class ProspectoCompradorSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    class Meta:
        model = ProspectoComprador
        fields = ('id', 'interested_phone_number', 'nombre', 'correo',
                  'inmueble' ,'created', 'updated', 'is_active')
        extra_kwargs = {'id': {'read_only': True}}
