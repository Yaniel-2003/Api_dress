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
    serializer_class = TiposPrendasSerializer
    queryset = TiposPrendas.objects.all().order_by('idprenda')


class TallaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TallasSerializer
    queryset = Tallas.objects.all().order_by('idtalla')


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