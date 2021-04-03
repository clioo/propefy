import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from apps.core import models
from apps.core.tests.test_model import sample_categoria, sample_municipio, sample_tipo_propiedad
from apps.utils.test_utils.utils import get_random_phone, get_random_username


def create_inmueble(**params):
    inmueble = models.Inmueble.objects.create(
            status='a',
            estacionamientos=2,
            recamaras=2,
            banos=2,
            medios_banos=2,
            latitud=1.33333,
            longitud=1.333333
        )
    """Create a sample user"""
    if not params.get('titulo'):
        params['titulo'] = 'Lorem ipsum mortem'
    if not params.get('descripcion'):
        params['descripcion'] = """Lorem ipsum mortem Lorem ipsum mortem
            Lorem ipsum mortem Lorem ipsum mortem Lorem ipsum mortem
            Lorem ipsum mortem"""
    if not params.get('categoria'):
        params['categoria'] = sample_categoria()
    if not params.get('tipo_propiedad'):
        params['tipo_propiedad'] = sample_tipo_propiedad()
    if not params.get('municipio'):
        params['municipio'] = sample_municipio()
    if not params.get('precio'):
        params['precio'] = 1000000
    if not params.get('status'):
        params['status'] = 'a'
    if not params.get('estacionamientos'):
        params['estacionamientos'] = 2
    if not params.get('recamaras'):
        params['recamaras'] = 2
    if not params.get('banos'):
        params['banos'] = 2
    if not params.get('medios_banos'):
        params['medios_banos'] = 2
    if not params.get('latitud'):
        params['latitud'] = 1.33333
    if not params.get('longitud'):
        params['longitud'] = 1.33333
    return get_user_model().objects.create_user(
        **params
    )


class PublicInmuebleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
