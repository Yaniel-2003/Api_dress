from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.catalogo import *


router = DefaultRouter()

router.register(r'genero', GeneroViewSet, basename='genero')
router.register(r'tipo-numero-documento', NumDocumentoViewSet, basename='tipo-numero-documento')
router.register(r'perfil', PerfilViewSet, basename='perfil')
router.register(r'marca', MarcaViewSet, basename='marca')
router.register(r'color', ColorViewSet, basename='color')
router.register(r'talla', TallaViewSet, basename='talla')
router.register(r'impuesto', ImpuestoViewSet, basename='impuesto')
router.register(r'descuento', DescuentoViewSet, basename='descuento')
router.register(r'cupon', CuponesViewSet, basename='cupon')
router.register(r'categoria', CategoriaViewSet, basename='categoria')

urlpatterns = [
    path('',include(router.urls)),
]