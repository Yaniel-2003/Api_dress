from django.urls import path, include


urlpatterns = [
    path('', include('core.urls.catalogo_urls')),
    path('', include('core.urls.auth_urls')),
    path('', include('core.urls.usuarios_urls')),
    path('', include('core.urls.direcciones_urls')),
    path('', include('core.urls.articulo_urls')),
]