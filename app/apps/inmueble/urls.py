from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
app_name = 'inmueble'
router.register('public/inmuebles', views.InmuebleViewSet, 'public-inmuebles')
router.register('random/inmuebles', views.RandomInmueblesViewSet, 'random-inmuebles')
router.register('inmuebles/history', views.HistorialViewSet, 'history')
router.register('public/tipo-inmueble', views.TipoInmuebleViewSet, 'tipo-inmueble')
router.register('public/municipios', views.MunicipioViewSet, 'municipios')
router.register('public/estados', views.EstadoViewSet, 'estados')


urlpatterns = []

urlpatterns += router.urls
