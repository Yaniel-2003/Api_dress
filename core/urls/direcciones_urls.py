from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.direcciones_views import DireccionesViewSet

router = DefaultRouter()

router.register(r'direcciones', DireccionesViewSet, basename='direcciones')

urlpatterns = [
    path('', include(router.urls)),
]