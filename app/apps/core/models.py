from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings
from propefy.storage_backend import PrivateMediaStorage
from .validators import validate_file_images
import os.path
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchVectorField, TrigramSimilarity
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.dispatch import receiver


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        abstract = True


class BaseProspectoModel(BaseModel):
    nombre = models.CharField(max_length=255)
    correo = models.CharField(max_length=255)
    interested_phone_number = models.CharField(max_length=10)
    inmueble = models.ForeignKey('Inmueble', on_delete=models.PROTECT)

    class Meta:
        abstract = True



class GenericModel(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creating a superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Customer user model that support using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=13)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['name']),
            models.Index(fields=['last_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['email', 'is_active']),
        ]


class Like(GenericModel):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)


class Likable(models.Model):
    likes = GenericRelation(Like)

    class Meta:
        abstract = True


class Categoria(models.Model):
    nombre = models.CharField(verbose_name="Categoría", max_length=255)

    def __str__(self):
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]

class TipoPropiedad(models.Model):
    nombre = models.CharField(max_length=255,verbose_name="Tipo")

    def __str__(self):
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]


class Estado(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    cve_entidad = models.CharField(max_length=255, unique=True)
    nombre_abreviacion = models.CharField(max_length=255)
    class Meta:
        ordering = ('nombre',)
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['nombre', 'cve_entidad']),
        ]

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    cve_municipio = models.IntegerField()
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    estado = models.ForeignKey('Estado', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('cve_municipio', 'estado')
        ordering = ('nombre',)
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['nombre', 'cve_municipio']),
        ]

    def __str__(self):
        return self.nombre


class Localidad(models.Model):
    ambitos = (
        ('U', 'Urbano'),
        ('R', 'Rural')
    )
    nombre = models.CharField(max_length=255)
    cve_localidad = models.IntegerField()
    ambito = models.CharField(max_length=5, choices=ambitos)
    municipio = models.ForeignKey('Municipio', on_delete=models.CASCADE)
    pob_total = models.IntegerField(null=True, blank=True)
    pob_masculina = models.IntegerField(null=True, blank=True)
    pob_femenina = models.IntegerField(null=True, blank=True)
    total_viviendas_habitadas = models.IntegerField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['nombre', 'cve_localidad']),
        ]


class Asentamiento(models.Model):
    name = models.CharField(max_length=255, verbose_name="d_asenta")
    tipo_asentamiento = models.CharField(max_length=255, verbose_name="d_tipo_asenta")
    zona = models.CharField(max_length=255, verbose_name="d_zona")
    ciudad = models.CharField(max_length=255, verbose_name="ciudad")
    codigo_postal = models.CharField(max_length=5, verbose_name='d_codigo')
    municipio = models.ForeignKey('Municipio', on_delete=models.CASCADE)
    id_asenta_cp = models.CharField(max_length=255, verbose_name="id_asenta_cpcons")
    polygon = gis_models.MultiPolygonField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('id_asenta_cp', 'codigo_postal')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['tipo_asentamiento']),
            models.Index(fields=['zona']),
            models.Index(fields=['ciudad']),
            models.Index(fields=['codigo_postal']),
            models.Index(fields=['municipio']),
        ]


class PrecioPeriodo(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Precio periodo")

    def __str__(self):
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
        ]


class Amenidades(models.Model):
    name = models.CharField(max_length=255)


class Dueno(models.Model):
    nombre = models.CharField(max_length=255)
    celular = models.CharField(max_length=255)

    class Meta:
        ordering = ('nombre',)
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['celular']),
        ]

    def __str__(self):
        return self.nombre


class Inmueble(Likable):
    status_choices = [
        ('a', 'En venta'),
        ('v', 'Vendida',),
    ]
    monedas_choices = [
        ('MXN', 'Pesos mexicanos'),
        ('USD', 'Dólar')
    ]
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    antiguedad = models.IntegerField(verbose_name="Años de antigüedad")
    dueno = models.ForeignKey('Dueno', null=True, on_delete=models.CASCADE)
    acepta_credito = models.BooleanField(null=True, default=None)
    categoria = models.ForeignKey('Categoria', verbose_name="Categoría", on_delete=models.PROTECT)
    tipo_propiedad = models.ForeignKey('TipoPropiedad', verbose_name="Tipo de propiedad", on_delete=models.PROTECT)
    municipio = models.ForeignKey('Municipio', on_delete=models.PROTECT)
    precio = models.FloatField(verbose_name="Precio")
    moneda = models.CharField(max_length=5, choices=monedas_choices, default='MXN')
    precio_periodo = models.ForeignKey('PrecioPeriodo', on_delete=models.PROTECT,
                                       null=True, blank=True)
    status = models.CharField(max_length=10, choices=status_choices,
                              default='a')
    estacionamientos = models.IntegerField(verbose_name="Estacionamientos")
    recamaras = models.IntegerField(verbose_name="recamaras")
    banos = models.IntegerField(verbose_name="Baños")
    medios_banos = models.IntegerField(verbose_name="Medios baños")
    m_2 = models.FloatField(null=True, verbose_name="Metros cuadrados totales")
    m_2_construccion = models.FloatField(null=True,
        verbose_name="Metros cuadrados de construcción")
    direccion = models.CharField(max_length=255)
    latitud = models.FloatField()
    longitud = models.FloatField()
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    destacado = models.BooleanField(default=False)
    dentro_de_privada = models.BooleanField(default=False,
        verbose_name="¿Está dentro de privada?")
    search_vector = SearchVectorField(null=True)
    point = gis_models.PointField(geography=True, blank=True)
    point_geometry = gis_models.PointField(geography=False, blank=True)
    views_counter = models.PositiveIntegerField(default=0)
    se_admiten_mascotas = models.BooleanField(default=False, verbose_name="¿Acepta mascotas?")
    amueblada = models.BooleanField(default=False)
    amenidades = models.ManyToManyField('Amenidades', blank=True)

    def save(self, **kwargs):
        self.point = Point(self.longitud, self.latitud)
        self.point_geometry = Point(self.longitud, self.latitud)
        super().save(**kwargs)

    def __str__(self):
        return self.titulo

    class Meta:
        indexes = [
            models.Index(fields=['titulo']),
            models.Index(fields=['descripcion']),
            models.Index(fields=['dueno']),
            models.Index(fields=['acepta_credito']),
            models.Index(fields=['categoria']),
            models.Index(fields=['tipo_propiedad']),
            models.Index(fields=['municipio']),
            models.Index(fields=['precio']),
            models.Index(fields=['moneda']),
            models.Index(fields=['precio_periodo']),
            models.Index(fields=['status']),
            models.Index(fields=['estacionamientos']),
            models.Index(fields=['recamaras']),
            models.Index(fields=['banos']),
            models.Index(fields=['medios_banos']),
            models.Index(fields=['direccion']),
            models.Index(fields=['search_vector']),
        ]


class Imagenes(models.Model):
    inmueble = models.ForeignKey('Inmueble', on_delete=models.CASCADE)
    photo = models.ImageField(storage=PrivateMediaStorage(),
                              validators=[validate_file_images],
                              verbose_name="Original image sent by user")
    thumbnail = models.ImageField(storage=PrivateMediaStorage(),
                                  validators=[validate_file_images],
                                  verbose_name="Thumbnail")

    def save(self, *args, **kwargs):
        if not self.thumbnail:
            self.make_thumbnail()
        return super().save(*args, **kwargs)

    def make_thumbnail(self):

        image = Image.open(self.photo)
        image.thumbnail((400, 400), Image.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.photo.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        return True


class HistorialVisitas(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, blank=True, null=True)
    inmueble = models.ForeignKey('Inmueble', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class HistorialBusquedas(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    recamaras = models.CharField(max_length=255, null=True)
    precio_min = models.CharField(max_length=255, null=True)
    precio_max = models.CharField(max_length=255, null=True)
    estado = models.CharField(max_length=255, null=True)
    full_text = models.CharField(max_length=255, null=True)
    titulo = models.CharField(max_length=255, null=True)
    descripcion = models.CharField(max_length=255, null=True)
    categoria = models.CharField(max_length=255, null=True)
    tipo_propiedad = models.CharField(max_length=255, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)


class SpamEmail(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=Inmueble)
def inmueble_post_save(sender, instance, created, *args, **kwargs):
    """Argument explanation:

       sender - The model class. (MyModel)
       instance - The actual instance being saved.
       created - Boolean; True if a new record was created.

       *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
    """
    if created:
        instance.search_vector = SearchVector('titulo', 'descripcion', 'direccion')
        instance.save()


class ProspectoVendedor(BaseProspectoModel):
    """Son quienes quieren vender su propiedad sin registrarse."""
    pass


class ProspectoComprador(BaseProspectoModel):
    """Son quienes deciden comprar sin registrarse"""
    pass
