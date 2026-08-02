from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..serializers import *
from ..models import *


#### MODELOS CRUD TABLAS CATALOGO 

class GeneroViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneroSerializer
    queryset = Genero.objects.all().order_by('idgenero')

class NumDocumentoViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = NunDocumentoSerializer
    queryset = NunDocumento.objects.all().order_by('idnumero')

class PerfilViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PerfilSerializer
    queryset = Perfil.objects.all().order_by('idperfil')


class MarcaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MarcasSerializer
    queryset = Marcas.objects.all().order_by('idmarca') 

class ColorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ColoresSerializer
    queryset = Colores.objects.all().order_by('idcolor')

class PrendaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PrendasSerializer
    queryset = Prendas.objects.all().order_by('idprenda')

class CatReglasTallajeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CatReglasTallajeSerializer
    queryset = Cat_Reglas_Tallaje.objects.all().order_by('idregla')


class TallaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TallasSerializer

    def get_queryset(self):
        queryset = Tallas.objects.all().order_by('idtalla')

        query = self.request.query_params

        prenda_id = query.get('prenda')

        if prenda_id:
            try:
                prenda = Prendas.objects.get(idprenda=prenda_id)
                queryset = queryset.filter(regla_tallaje=prenda.regla_tallaje)

            except Prendas.DoesNotExist:
                queryset = Tallas.objects.none()
            
        return queryset
        


class ImpuestoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ImpuestosSerializer
    queryset = Impuestos.objects.all().order_by('idimpuesto')


class DescuentoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DescuentosSerializer
    queryset = Descuentos.objects.all().order_by('iddescuento')  


class CuponesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CuponesSerializer
    queryset = Cupones.objects.all().order_by('idcupon')


class CategoriaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Categoria.objects.select_related('genero', 'padre').order_by('nombre') 

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CategoriaWriteSerializer
        return CategoriaListSerializer