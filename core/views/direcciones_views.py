from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from ..serializers import DireccionesListSerializer, DireccionesWriteSerializer
from ..models import Direcciones

class DireccionesViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Direcciones.objects.select_related('usuario').order_by('-usuario')

        query = self.request.query_params
        
        buscar = query.get('buscar') 

        if(buscar):
            queryset = queryset.filter(
                Q(Usuario__nombres__icontains=buscar) |
                Q(Usuario__numero__icontains=buscar) |
                Q(Usuario__documento__sigla__icontains=buscar)
            )

        return queryset


    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'update'):
            return DireccionesWriteSerializer
        return DireccionesListSerializer 