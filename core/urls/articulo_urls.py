from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.articulos_views import ArticulosViewSet, VariantesArticulosViewSet, Fotos_articulos, ArticuloDescuentoViewSet


router = DefaultRouter()

router.register(r'articulos', ArticulosViewSet, basename='articulos')
router.register(r'variantes-articulos', VariantesArticulosViewSet, basename='variantes-articulos')
router.register(r'descuento-articulos', ArticuloDescuentoViewSet, basename='descuento-articulos')

urlpatterns = [
    path('', include(router.urls)),
    path('variantes/<uuid:idvararticulo>/fotos/', Fotos_articulos, name=('fotos-variantes')),
]