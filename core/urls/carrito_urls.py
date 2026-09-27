from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import carritoViewSet

router = DefaultRouter()

router.register(r'carritos-compras', carritoViewSet, basename='carritos-compras')

urlpatterns = [
    path('', include(router.urls)),
    path('agregar_item_carrito/<uuid:idvararticulo>/', carritoViewSet.as_view({'post': 'agregar_item_carrito'}), name='agregar_item_carrito'),
]