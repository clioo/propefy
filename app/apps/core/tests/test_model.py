from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.core import models


def sample_user(email='test@test.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(
        email, password
    )


def sample_categoria(nombre='Venta'):
    return models.Categoria.objects.create(nombre=nombre)


def sample_tipo_propiedad(nombre='Casa habitación'):
    return models.TipoPropiedad.objects.create(nombre=nombre)


def sample_municipio(nombre='Ahome', **kwargs):
    estado = models.Estado.objects.all()
    if estado.exists():
        estado = estado.first()
    else:
        estado = models.Estado.objects.create(nombre='Sinaloa',
                                              cve_entidad='sla',
                                              nombre_abreviacion='asd')
    return models.Municipio.objects.create(estado=estado,
                                           nombre=nombre,
                                           **kwargs)


def sample_precio_periodo(nombre='Mensual'):
    return models.PrecioPeriodo.objects.create(nombre=nombre)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        email = 'test@test.com'
        password = 'passSssS123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email, "email is not {0}".format(email))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@Test.com'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())
        pass

    def test_new_user_invalid_email(self):
        """Teste creating user with no email error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new super user"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_inmueble_venta(self):
        """Test creating a new property"""
        categoria = sample_categoria()
        tipo = sample_tipo_propiedad(nombre='Renta')
        municipio = sample_municipio(cve_municipio='12')
        titulo = 'Vivienda de dos recamaras'
        descripcion = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
         do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
         Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
         nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in 
         reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur. Excepteur sint occaecat cupidatat non proident, sunt in 
          culpa qui officia deserunt mollit anim id est laborum.
        """
        inmueble = models.Inmueble.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            categoria=categoria,
            tipo_propiedad=tipo,
            municipio=municipio,
            precio=100000,
            status='a',
            estacionamientos=2,
            recamaras=2,
            banos=2,
            medios_banos=2,
            latitud=1.33333,
            longitud=1.333333
        )
        self.assertEqual(str(inmueble), inmueble.titulo)

    def test_create_inmueble_renta(self):
        """Test creating a new property"""
        categoria = sample_categoria('Renta')
        tipo = sample_tipo_propiedad(nombre='Vivienda')
        municipio = sample_municipio(cve_municipio='12')
        titulo = 'Vivienda de dos recamaras'
        precio_periodo = sample_precio_periodo()
        descripcion = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
         do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
         Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
         nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in 
         reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur. Excepteur sint occaecat cupidatat non proident, sunt in 
          culpa qui officia deserunt mollit anim id est laborum.
        """
        inmueble = models.Inmueble.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            categoria=categoria,
            tipo_propiedad=tipo,
            municipio=municipio,
            precio=100000,
            precio_periodo=precio_periodo,
            status='a',
            estacionamientos=2,
            recamaras=2,
            banos=2,
            medios_banos=2,
            latitud=1.33333,
            longitud=1.333333
        )
        self.assertEqual(str(inmueble), inmueble.titulo)
