from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from datetime import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from rest_framework.decorators import api_view, parser_classes, permission_classes, action
import os

from ..serializers import ArticulosListSerializer, ArticulosWriteSerializer, VariantesArticulosListSerializer, VariantesArticulosWriteSerializer, ArticuloDescuentoSerializer, ArticuloDescuentoWriteSerializer, VarianteArticulosSerializers
from ..models import Articulos, VariantesArticulos, ArticuloDescuento, FotoVarianteArticulo, Cat_Reglas_Tallaje, Prendas, Tallas
from ..paginacion import PaginacionGlobal


class ArticulosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = PaginacionGlobal

    def get_queryset(self):
        queryset = Articulos.objects.select_related(
            'marca', 
            'categoria', 
            'impuestos'
        ).order_by('estado')
        
        query = self.request.query_params

        busqueda = query.get('buscar')

        if(busqueda):
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |  
                Q(slug__icontains=busqueda) |
                Q(marca__nombre__icontains=busqueda) | 
                Q(marca__slug__icontains=busqueda) | 
                Q(categoria__nombre__icontains=busqueda) | 
                Q(categoria__slug__icontains=busqueda)
            )

        marca_id = query.get('marca')
        categoria_id = query.get('categoria')
        estado_articulo = query.get('estado')

        if marca_id:
            queryset = queryset.filter(marca_id=marca_id)

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        if estado_articulo is not None:
            es_activo = estado_articulo.lower() in ['true', '1' ,'yes']
            queryset = queryset.filter(estado=es_activo)


        return queryset
    


    
    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ArticulosWriteSerializer
        return ArticulosListSerializer
    



class VariantesArticulosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = PaginacionGlobal

    def get_queryset(self):
        queryset = VariantesArticulos.objects.select_related(
            'articulo',
            'articulo__prendas',
            'articulo__marca',
            'articulo__categoria',
            'articulo__impuestos',
            'color',
            'talla'
        ).order_by('idvararticulo')

        query = self.request.query_params

        busqueda = query.get('buscar')
        color_id = query.get('color')
        talla_id = query.get('talla')
        marca_id = query.get('marca')
        categoria_id = query.get('categoria')
        prendas_id = query.get('prendas')
        estado_articulo = query.get('estado')

        if busqueda:
            queryset = queryset.filter(
                Q(articulo__nombre__icontains=busqueda) |
                Q(articulo__slug__icontains=busqueda) |
                Q(articulo__marca__nombre__icontains=busqueda) |
                Q(articulo__categoria__nombre__icontains=busqueda) |
                Q(sku__icontains=busqueda)
            )


        if color_id:
            queryset = queryset.filter(color_id__in=color_id.split(','))

        if prendas_id:
            queryset = queryset.filter(articulo__prendas_id__in=prendas_id.split(','))

        if talla_id:
            queryset = queryset.filter(talla_id__in=talla_id.split(','))

        if marca_id:
            queryset = queryset.filter(articulo__marca_id__in=marca_id.split(','))

        if categoria_id:
            queryset = queryset.filter(articulo__categoria_id__in=categoria_id.split(','))

        if estado_articulo:
            es_activo = estado_articulo.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(articulo__estado=es_activo)

        return queryset


    def get_serializer_class(self):
        if self.action == 'tienda_publica':
            return VarianteArticulosSerializers
        
        if self.action in ('create', 'update', 'partial_update'):
            return VariantesArticulosWriteSerializer
        return VariantesArticulosListSerializer

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny])
    def tienda_publica(self, request):
        queryset = self.get_queryset() 

        queryset = queryset.filter(stock__gt=0, articulo__estado=True)

        queryset = queryset.prefetch_related(
            'articulodescuento_set',
            'articulodescuento_set__descuento'
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

EXTENSIONES = ['.jpg', '.png', '.jpeg']

@api_view(['POST', 'GET', 'PUT'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])

def Fotos_articulos(request, idvararticulo):
    try:
        fotos_articulos = VariantesArticulos.objects.get(idvararticulo=idvararticulo)
    except VariantesArticulos.DoesNotExist:
        return Response({'error': 'No se econtraron las fotos'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        fotos = fotos_articulos.fotovariantearticulo_set.all()

        data = [{
            'id': foto.idfoto,
            'url': request.build_absolute_url(foto.archivo.url),
        } for foto in fotos
        ]
        return Response(data, status=status.HTTP_200_OK)
    
    """ if request.method == 'POST':
        fotos_guardadas = []
        errores = []

        for i in range (4):
            archivo = request.FILES.get(f'foto{i}')

            if not archivo: continue

            ext = os.path.splitext(archivo.name)[1].lower()

            if ext not in EXTENSIONES:
                errores.append(f"Foto{i}: extension no permitida") 
                continue

            foto = FotoVarianteArticulo(variante_articulo=fotos_articulos)

            foto.archivo.save(archivo.name, archivo, save=True)

            fotos_guardadas.append({
                'id': foto.idfoto
            })

    return Response({'fotos_guardadas': fotos_guardadas, 'errores':errores}, status=status.HTTP_201_CREATED) """





class ArticuloDescuentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = PaginacionGlobal

    def get_queryset(self):
        queryset = ArticuloDescuento.objects.select_related(
            'vararticulo',
            'descuento'
        ).order_by('-descuento')

        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ArticuloDescuentoWriteSerializer
        return ArticuloDescuentoSerializer