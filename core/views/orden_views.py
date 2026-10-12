from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from ..serializers import ItemsOrdenListSerializer, OrdenListSerializer, OrdenWriteSerializer
from ..models import Orden, ItemsOrden


class OrdenViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Orden.objects
                .filter(usuario=self.request.user)
                .select_related('usuario','direccion')
                .prefetch_related('itemsorden_set__vararticulo')
                .order_by('-fecha_creacion'))

    def get_serializer_class(self):
        if self.action == 'create':
            return OrdenWriteSerializer
        return OrdenListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        orden = serializer.save()
        data = OrdenListSerializer(orden, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED)
    
        