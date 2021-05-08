import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from apps.core import models
from apps.core.tests.test_model import (sample_categoria, sample_municipio,
                                        sample_tipo_propiedad,
                                        sample_precio_periodo,
                                        sample_user)
from apps.utils.test_utils.utils import get_random_phone, get_random_username


INMUEBLES_URL = reverse('inmueble:public-inmuebles-list')
MUNICIPIOS_URL = reverse('inmueble:municipios-list')
ESTADOS_URL = reverse('inmueble:estados-list')
TIPO_INMUEBLE_URL = reverse('inmueble:tipo-inmueble-list')
HISTORIA_INMUEBLE_URL = reverse('inmueble:history-list')


def get_detail_inmueble_url(id: int):
    return reverse('inmueble:public-inmuebles-detail', args=[id,])


def create_inmueble(**params):
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
        params['municipio'] = sample_municipio(cve_municipio='12')
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
    return models.Inmueble.objects.create(**params)


class PublicInmuebleTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_ciudad_success(self):
        res = self.client.get(MUNICIPIOS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_estados_success(self):
        res = self.client.get(ESTADOS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_tipo_inmueble_success(self):
        res = self.client.get(TIPO_INMUEBLE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_inmueble_simple_success(self):
        precio_periodo_mensual = sample_precio_periodo(nombre='Mensual')
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        tipo_local_comercial = sample_tipo_propiedad(nombre='Locales comerciales')
        categoria_venta = sample_categoria(nombre='Venta')
        categoria_renta = sample_categoria(nombre='Renta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        municipio_culiacan = sample_municipio(nombre='Culiacán', cve_municipio='13')
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta,
                        municipio=municipio_ahome, precio=1000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_ahome, precio=10000)
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta,
                        municipio=municipio_culiacan, precio=2000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_culiacan, precio=15000)
        res = self.client.get(INMUEBLES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('results')), 4)

    def test_filter_inmueble_success(self):
        precio_periodo_mensual = sample_precio_periodo(nombre='Mensual')
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        tipo_local_comercial = sample_tipo_propiedad(nombre='Locales comerciales')
        categoria_venta = sample_categoria(nombre='Venta')
        categoria_renta = sample_categoria(nombre='Renta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        municipio_culiacan = sample_municipio(nombre='Culiacán', cve_municipio='13')
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta,
                        municipio=municipio_ahome, precio=1000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_ahome, precio=10000)
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta,
                        municipio=municipio_culiacan, precio=2000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_culiacan, precio=15000)
        res = self.client.get(INMUEBLES_URL, {'municipio': municipio_ahome.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('results')), 2)
        res = self.client.get(INMUEBLES_URL, {'tipo_propiedad': tipo_casa_habitacion.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('results')), 2)

    def test_history_created_user_anonymous_success(self):
        """Test that history is created when retrieving a detail inmueble"""
        precio_periodo_mensual = sample_precio_periodo(nombre='Mensual')
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        tipo_local_comercial = sample_tipo_propiedad(nombre='Locales comerciales')
        categoria_venta = sample_categoria(nombre='Venta')
        categoria_renta = sample_categoria(nombre='Renta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        municipio_culiacan = sample_municipio(nombre='Culiacán', cve_municipio='13')
        inmueble1 = create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                                    categoria=categoria_venta,
                                    municipio=municipio_ahome, precio=1000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_ahome, precio=10000)
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta,
                        municipio=municipio_culiacan, precio=2000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_culiacan, precio=15000)
        res = self.client.get(get_detail_inmueble_url(inmueble1.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(models.HistorialVisitas.objects.count(), 1)


class PrivateInmuebleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_history_logged_user_success(self):
        precio_periodo_mensual = sample_precio_periodo(nombre='Mensual')
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        tipo_local_comercial = sample_tipo_propiedad(nombre='Locales comerciales')
        categoria_venta = sample_categoria(nombre='Venta')
        categoria_renta = sample_categoria(nombre='Renta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        municipio_culiacan = sample_municipio(nombre='Culiacán', cve_municipio='13')
        inmueble1 = create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                                    categoria=categoria_venta,
                                    municipio=municipio_ahome, precio=1000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_ahome, precio=10000)
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta,
                        municipio=municipio_culiacan, precio=2000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_culiacan, precio=15000)
        res = self.client.get(get_detail_inmueble_url(inmueble1.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(models.HistorialVisitas.objects.count(), 1)
        history = models.HistorialVisitas.objects.first()
        self.assertEqual(history.user.id, self.user.id)

    def test_history_endpoint_success(self):
        precio_periodo_mensual = sample_precio_periodo(nombre='Mensual')
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        tipo_local_comercial = sample_tipo_propiedad(nombre='Locales comerciales')
        categoria_venta = sample_categoria(nombre='Venta')
        categoria_renta = sample_categoria(nombre='Renta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        municipio_culiacan = sample_municipio(nombre='Culiacán', cve_municipio='13')
        inmueble1 = create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                                    categoria=categoria_venta,
                                    municipio=municipio_ahome, precio=1000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_ahome, precio=10000)
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta,
                        municipio=municipio_culiacan, precio=2000000)
        create_inmueble(tipo_propiedad=tipo_local_comercial,
                        categoria=categoria_renta,
                        precio_periodo=precio_periodo_mensual,
                        municipio=municipio_culiacan, precio=15000)
        # Getting house dtails with first user
        res = self.client.get(get_detail_inmueble_url(inmueble1.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(models.HistorialVisitas.objects.count(), 1)
        # Getting house dtails with second user
        user = sample_user(email='asdasd@test.com')
        self.client.force_authenticate(user)
        res = self.client.get(get_detail_inmueble_url(inmueble1.id))
        self.assertEqual(models.HistorialVisitas.objects.count(), 2)
        # Retriving history
        res = self.client.get(HISTORIA_INMUEBLE_URL)
        self.assertEqual(len(res.data.get('results')), 1)
