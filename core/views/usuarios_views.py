from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q

from ..models import Usuario
from ..serializers import UsuarioListSerializer, UsuarioWriteSerializer

class UsuariosViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # El registro es publico 
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    def get_queryset(self):
        queryset = Usuario.objects.select_related('perfil', 'documento').order_by('fecha_creacion')

        # Fltros dinamicos

        query = self.request.query_params

        busqueda = query.get('buscar')

        if busqueda:
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(apellido__icontains=busqueda) |
                Q(email__icontains=busqueda) |
                Q(numero__icontains=busqueda)
            )

        tipo_doc = query.get('documento')
        perfil = query.get('nombre')

        if tipo_doc:
            queryset = queryset.filter(NunDocumento__sigla__icontains=tipo_doc)

        if perfil:
            queryset = queryset.filter(Perfil__nombre__icontains=perfil)

        return queryset
    
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return UsuarioWriteSerializer
        return UsuarioListSerializer
        
