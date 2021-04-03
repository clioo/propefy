from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
app_name = 'inmuebe'
router.register('public/inmuebles', views.InmuebleViewSet, 'public-inmuebles')

urlpatterns = []

urlpatterns += router.urls
