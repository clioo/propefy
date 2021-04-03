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


class Categoria(models.Model):
    nombre = models.CharField(verbose_name="Categoría", max_length=255)

    def __str__(self):
        return self.nombre


class TipoPropiedad(models.Model):
    nombre = models.CharField(max_length=255,verbose_name="Tipo")

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    estado = models.ForeignKey('Estado', on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre


class PrecioPeriodo(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Precio periodo")

    def __str__(self):
        return self.nombre


class Amenidades(models.Model):
    pass


class Dueno(models.Model):
    nombre = models.CharField(max_length=255)
    celular = models.CharField(max_length=255)

def __str__(self):
    return self.nombre


class Inmueble(models.Model):
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
    direccion = models.CharField(max_length=255)
    latitud = models.FloatField()
    longitud = models.FloatField()
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo


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
        image.thumbnail((100, 100), Image.ANTIALIAS)

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
