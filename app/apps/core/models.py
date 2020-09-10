from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(verbose_name="Categoría", max_length=255)


class TipoPropiedad(models.Model):
    nombre = models.CharField(verbose_name="Tipo")


class Estado(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")


class Municipio(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Nombre")
    estado = models.ForeignKey('Estado')


class PrecioPerido(models.Model):
    nombre = models.CharField(max_length=255, verbose_name="Precio periodo")


class Imagenes(models.Model):
    inmueble = models.ForeignKey('Inmueble', on_delete=models.PROTECT)
    imagen = models.ImageField()


class Inmueble(models.Model):
    status_choices = [
        ('v', 'Vendida',),
    ]
    categoria = models.ForeignKey('Categoria', verbose_name="Categoría")
    tipo_propiedad = models.ForeignKey('TipoPropiedad', verbose_name="Tipo de propiedad")
    municipio = models.ForeignKey('Municipio', on_delete=models.PROTECT)
    precio = models.FloatField(verbose_name="")
    precio_periodo = models.ForeignKey('PrecioPeriodo', on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=status_choices,
                              blank=True)
    estacionamientos = models.IntegerField(verbose_name="Estacionamientos")
    ambientes = models.IntegerField(verbose_name="Ambientes")
    banos = models.IntegerField(verbose_name="Baños")
    banos_banos = models.IntegerField(verbose_name="Baños")
    latitud = models.FloatField()
    longitud = models.FloatField()
    vendida = models.BooleanField(default=False)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
