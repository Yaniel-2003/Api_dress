from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import api_view, parser_classes, permission_classes, action

from ..serializers import CarritoListSerializer, ItemsCarritoListSerializer, ItemsOrdenListSerializer, ItemsCarritoWriteSerializer
from ..models import Carrito, ItemsCarrito, VariantesArticulos


class carritoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        queryset = ItemsCarrito.objects.select_related(
            'carrito__usuario',
            'vararticulo'
        ).filter(carrito__usuario=self.request.user).order_by('iditmcarrito')

        return queryset

    @action(detail=False, methods=['POST'])
    def agregar_item_carrito(self, request, idvararticulo):
        vararticulo = VariantesArticulos.objects.get(idvararticulo=idvararticulo)

        carrito, creado = Carrito.objects.get_or_create(
            usuario=request.user
        )

        item, creado = ItemsCarrito.objects.get_or_create(
            carrito=carrito,
            vararticulo=vararticulo,
            defaults={'cantidad': 1}
        )

        if not creado:
            item.cantidad += 1
            item.save()


        return Response(ItemsCarritoListSerializer(item).data, status=status.HTTP_201_CREATED)


    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return ItemsCarritoWriteSerializer
        return ItemsCarritoListSerializer 