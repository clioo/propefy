from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


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
    phone = models.CharField(max_length=10)
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


class Imagenes(models.Model):
    inmueble = models.ForeignKey('Inmueble', on_delete=models.PROTECT)
    imagen = models.ImageField()


class Amenidades(models.Model):
    pass


class Inmueble(models.Model):
    status_choices = [
        ('a', 'En venta'),
        ('v', 'Vendida',),acosta
    ]
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    # tipo_transaccion
    # acepta_credito
    categoria = models.ForeignKey('Categoria', verbose_name="Categoría", on_delete=models.PROTECT)
    tipo_propiedad = models.ForeignKey('TipoPropiedad', verbose_name="Tipo de propiedad", on_delete=models.PROTECT)
    municipio = models.ForeignKey('Municipio', on_delete=models.PROTECT)
    precio = models.FloatField(verbose_name="")
    # moneda
    precio_periodo = models.ForeignKey('PrecioPeriodo', on_delete=models.PROTECT,
                                       blank=True, null=True)
    status = models.CharField(max_length=10, choices=status_choices,
                              blank=True)
    estacionamientos = models.IntegerField(verbose_name="Estacionamientos")
    ambientes = models.IntegerField(verbose_name="Ambientes")
    banos = models.IntegerField(verbose_name="Baños")
    medios_banos = models.IntegerField(verbose_name="Medios baños")
    latitud = models.FloatField()
    longitud = models.FloatField()
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo
