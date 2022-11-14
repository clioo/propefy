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
from apps.core.models import SpamEmail


INMUEBLES_URL = reverse('inmueble:public-inmuebles-list')
RANDOM_INMUEBLES_URL = reverse('inmueble:random-inmuebles-list')
MUNICIPIOS_URL = reverse('inmueble:municipios-list')
ESTADOS_URL = reverse('inmueble:estados-list')
TIPO_INMUEBLE_URL = reverse('inmueble:tipo-inmueble-list')
HISTORIA_INMUEBLE_URL = reverse('inmueble:history-list')
MY_FAVORITE_INMUEBLES = reverse('inmueble:like-list')
PROSPECTO_COMPRADOR = reverse('inmueble:prospecto-comprador-list')
PROSPECTO_VENDEDOR = reverse('inmueble:prospecto-vendedor-list')


def get_dummy_inmueble() -> models.Inmueble:
    tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
    categoria_venta = sample_categoria(nombre='Venta')
    municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
    return create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                            categoria=categoria_venta,
                            municipio=municipio_ahome, precio=1000000)


def get_detail_inmueble_url(id: int) -> str:
    return reverse('inmueble:public-inmuebles-detail', args=[id,])


def patch_perform_like_inmueble(_id: int) -> str:
    return reverse('inmueble:like-detail', args=[_id])


def get_detail_prospecto_comprador_url(_id: int) -> str:
    return reverse('inmueble:prospecto-comprador-detail', args=[_id])


def get_detail_prospecto_vendedor_url(_id: int) -> str:
    return reverse('inmueble:prospecto-vendedor-detail', args=[_id])


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
    if not params.get('antiguedad'):
        params['antiguedad'] = 5
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
        self.assertEqual(len(res.data), 4)

    def test_list_random_inmueble_simple_success(self):
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
        res = self.client.get(RANDOM_INMUEBLES_URL, {'limit': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get('results')), 1)

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
        self.assertEqual(len(res.data), 2)
        res = self.client.get(INMUEBLES_URL, {'tipo_propiedad': tipo_casa_habitacion.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

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

    def test_inmueble_es_privada(self):
        precio_periodo_mensual = sample_precio_periodo(nombre='Mensual')
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        tipo_local_comercial = sample_tipo_propiedad(nombre='Locales comerciales')
        categoria_venta = sample_categoria(nombre='Venta')
        categoria_renta = sample_categoria(nombre='Renta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        municipio_culiacan = sample_municipio(nombre='Culiacán',
            cve_municipio='13')
        create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                        categoria=categoria_venta, dentro_de_privada=True,
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
        res = self.client.get(INMUEBLES_URL, {'dentro_de_privada': True})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)


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

    def test_view_counter_success(self):
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        categoria_venta = sample_categoria(nombre='Venta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        inmueble1 = create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                                    categoria=categoria_venta,
                                    municipio=municipio_ahome, precio=1000000)
        res = self.client.get(get_detail_inmueble_url(inmueble1.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('views_counter'), 1)
        res = self.client.get(get_detail_inmueble_url(inmueble1.id))
        self.assertEqual(res.data.get('views_counter'), 2)

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

    def test_inmueble_like_success(self):
        precio_periodo_mensual = sample_precio_periodo(nombre='Mensual')
        tipo_casa_habitacion = sample_tipo_propiedad(nombre='Casa habitación')
        tipo_local_comercial = sample_tipo_propiedad(nombre='Locales comerciales')
        categoria_venta = sample_categoria(nombre='Venta')
        categoria_renta = sample_categoria(nombre='Renta')
        municipio_ahome = sample_municipio(nombre='Ahome', cve_municipio='12')
        municipio_culiacan = sample_municipio(nombre='Culiacán',
                                              cve_municipio='13')
        inmueble1 = create_inmueble(tipo_propiedad=tipo_casa_habitacion,
                                    categoria=categoria_venta,
                                    municipio=municipio_ahome, precio=1000000)
        inmueble2 = create_inmueble(
            tipo_propiedad=tipo_local_comercial,
            categoria=categoria_renta,
            precio_periodo=precio_periodo_mensual,
            municipio=municipio_ahome, precio=10000)
        inmueble3 = create_inmueble(
            tipo_propiedad=tipo_casa_habitacion,
            categoria=categoria_venta,
            municipio=municipio_culiacan, precio=2000000)
        create_inmueble(
            tipo_propiedad=tipo_local_comercial,
            categoria=categoria_renta,
            precio_periodo=precio_periodo_mensual,
            municipio=municipio_culiacan, precio=15000)
        like_url = patch_perform_like_inmueble(inmueble1.id)
        like_url_inmueble_2 = patch_perform_like_inmueble(inmueble2.id)
        like_url_inmueble_3 = patch_perform_like_inmueble(inmueble3.id)
        res = self.client.patch(like_url, data={})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(like_url_inmueble_2, data={})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.patch(like_url_inmueble_3, data={})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        liked_inmueble = models.Inmueble.objects.get(id=inmueble1.id)
        likes = liked_inmueble.likes.all()
        self.assertEqual(len(likes), 1)
        res = self.client.get(MY_FAVORITE_INMUEBLES)
        self.assertEqual(len(res.data.get('results')), 3)

    def test_filter_search_history_inmueble_success(self):
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
        search_params = {
            'recamaras': 2,
            'precio_min': 100000,
            'precio_max': 50000,
            'estado': municipio_ahome.estado.id,
            'full_text': 'this is a full text search',
            'titulo': 'this is a title',
            'descripcion': 'this is a description',
            'categoria': categoria_renta.id,
            'tipo_propiedad': tipo_local_comercial.id,
            'latitude': 0.0,
            'longitude': 0.0,
            'antiguedad_min': 5,
            'antiguedad_max': 5,
        }
        res = self.client.get(INMUEBLES_URL, search_params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        historial_busqueda = models.HistorialBusquedas.objects.all().first()
        self.assertIsNotNone(historial_busqueda.recamaras)
        self.assertIsNotNone(historial_busqueda.precio_min)
        self.assertIsNotNone(historial_busqueda.precio_max)
        self.assertIsNotNone(historial_busqueda.estado)
        self.assertIsNotNone(historial_busqueda.full_text)
        self.assertIsNotNone(historial_busqueda.titulo)
        self.assertIsNotNone(historial_busqueda.descripcion)
        self.assertIsNotNone(historial_busqueda.categoria)
        self.assertIsNotNone(historial_busqueda.tipo_propiedad)
        self.assertIsNotNone(historial_busqueda.latitude)
        self.assertIsNotNone(historial_busqueda.longitude)


class ProspectoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_prospecto_compra_create_success(self):
        self.client.logout()
        inmueble = get_dummy_inmueble()
        payload = {
            "nombre": "Juan",
            'correo': 'jesus_acosta1996@hotmail.com',
            'interested_phone_number': '6681596072',
            'inmueble': inmueble.id,
        }
        res = self.client.post(PROSPECTO_COMPRADOR, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_prospecto_compra_list_normal_user_error(self):
        self.client.logout()
        res = self.client.get(PROSPECTO_COMPRADOR)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_prospecto_compra_retrieve_normal_user_error(self):
        self.client.logout()
        inmueble = get_dummy_inmueble()
        pros = models.ProspectoComprador.objects.create(
            interested_phone_number='6681596072',
            inmueble=inmueble
        )
        url = get_detail_prospecto_comprador_url(pros.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_prospecto_compra_list_admin_user_success(self):
        user = sample_user(email='test1@test.com', is_staff=True)
        self.client.force_authenticate(user)
        res = self.client.get(PROSPECTO_COMPRADOR)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_prospecto_compra_retrieve_admin_user_success(self):
        user = sample_user(email='test1@test.com', is_staff=True)
        self.client.force_authenticate(user)
        inmueble = get_dummy_inmueble()
        pros = models.ProspectoComprador.objects.create(
            interested_phone_number='6681596072',
            inmueble=inmueble
        )
        url = get_detail_prospecto_comprador_url(pros.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
