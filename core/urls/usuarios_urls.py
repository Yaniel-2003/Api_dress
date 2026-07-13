from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views.usuarios_views import UsuariosViewSet


router = DefaultRouter()

router.register(r'usuario', UsuariosViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
]