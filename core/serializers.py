from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import *

#### TABLAS CATALOGO 

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = "__all__"

class PerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfil
        fields = "__all__"

class NunDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NunDocumento
        fields = "__all__"

class MarcasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marcas
        fields = "__all__"

class ColoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Colores
        fields = "__all__"

class TallasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tallas
        fields = "__all__"

class ImpuestosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impuestos
        fields = "__all__"

class DescuentosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuentos
        fields = "__all__"

class CuponesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupones
        fields = "__all__"


#### CATEGORIAS

class CategoriaListSerializer(serializers.ModelSerializer):
    genero = GeneroSerializer(read_only=True)
    padre = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = "__all__"
        depth = 1

        def get_padre(self, obj):
            if obj.padre:
                return {
                    "id": obj.padre.categoria,
                    "nombre": obj.padre.nombre
                }
            return None

class CategoriaWriteSerializer(serializers.ModelSerializer):
    genero = serializers.PrimaryKeyRelatedField(queryset=Genero.objects.all())
    padre = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Categoria
        fields = ['idcategoria', 'genero', 'padre', 'nombre', 'slug', 'estado']


#### USUARIOS Y DIRECCIONES 

class UsuarioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"

class UsuarioWriteSerializer(serializers.ModelSerializer):
    perfil = serializers.PrimaryKeyRelatedField(queryset=Perfil.objects.all(), required=False)

    class Meta:
        model = Usuario
        fields = ['idusuario', 'email', 'nombres', 'apellidos', 'documento', 'numero', 'perfil', 'telefono', 'activo','password_hash']

    def create(self, validate_data):
        if 'password_hash' in validate_data:
            validate_data['password_hash'] = make_password(validate_data['password_hash'])
        return super().create(validate_data)


class DireccionesListSerializer(serializers.ModelSerializer):
    usuario = UsuarioListSerializer(read_only=True)

    class Meta:
        model = Direcciones
        fields = "__all__"

class DireccionesWriteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Direcciones
        fields = ['iddireccion', 'usuario', 'nombre_destinatario', 'direccion', 'residencia', 'barrio', 'ciudad', 'departamento', 'pais', 'codigo_postal', 'principal']


#### CATÁLOGO DE PRODUCTOS 

class ArticulosListSerializer(serializers.ModelSerializer):
    marca = MarcasSerializer(read_only=True)
    categoria = CategoriaListSerializer(read_only=True)
    impuestos = ImpuestosSerializer(read_only=True)

    class Meta:
        model = Articulos
        fields = "__all__"

class ArticulosWriteSerializer(serializers.ModelSerializer):
    marca = serializers.PrimaryKeyRelatedField(queryset=Marcas.objects.all())
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())
    impuestos = serializers.PrimaryKeyRelatedField(queryset=Impuestos.objects.all())

    class Meta:
        model = Articulos
        fields = ['idarticulo', 'marca', 'categoria', 'impuestos', 'nombre', 'slug', 'descripcion', 'precio_base', 'estado']


class VariantesArticulosListSerializer(serializers.ModelSerializer):
    articulo = ArticulosListSerializer(read_only=True)
    color = ColoresSerializer(read_only=True)
    talla = TallasSerializer(read_only=True)

    class Meta:
        model = VariantesArticulos
        fields = "__all__"

class VariantesArticulosWriteSerializer(serializers.ModelSerializer):
    articulo = serializers.PrimaryKeyRelatedField(queryset=Articulos.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=Colores.objects.all())
    talla = serializers.PrimaryKeyRelatedField(queryset=Tallas.objects.all())

    class Meta:
        model = VariantesArticulos
        fields = ['idvararticulo', 'articulo', 'color', 'talla', 'sku', 'stock', 'precio_extra', 'foto']

class ArticuloDescuentoSerializer(serializers.ModelSerializer):
    vararticulo = VariantesArticulosListSerializer(read_only=True)
    descuento = DescuentosSerializer(read_only=True)

    class Meta:
        model = ArticuloDescuento
        fields = "__all__"


#### CARRITO DE COMPRAS 

class ItemsCarritoListSerializer(serializers.ModelSerializer):
    vararticulo = VariantesArticulosListSerializer(read_only=True)

    class Meta:
        model = ItemsCarrito
        fields = "__all__"

class CarritoListSerializer(serializers.ModelSerializer):
    usuario = UsuarioListSerializer(read_only=True)
    items = ItemsCarritoListSerializer(source='itemscarrito_set', many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = ['idcarrito', 'usuario', 'creado_en', 'actualizado_en', 'items']

class ItemsCarritoWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemsCarrito
        fields = ['carrito', 'vararticulo', 'cantidad']


# --- ÓRDENES ---

class ItemsOrdenListSerializer(serializers.ModelSerializer):
    vararticulo = VariantesArticulosListSerializer(read_only=True)
    descuento = DescuentosSerializer(read_only=True)
    class Meta:
        model = ItemsOrden
        fields = '__all__'

class OrdenListSerializer(serializers.ModelSerializer):
    usuario = UsuarioListSerializer(read_only=True)
    direccion = DireccionesListSerializer(read_only=True)
    items = ItemsOrdenListSerializer(source='itemsorden_set', many=True, read_only=True)
    class Meta:
        model = Orden
        fields = '__all__'

class OrdenWriteSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    direccion = serializers.PrimaryKeyRelatedField(queryset=Direcciones.objects.all())
    cupon = serializers.PrimaryKeyRelatedField(queryset=Cupones.objects.all(), required=False, allow_null=True)
    
    class Meta:
        model = Orden
        fields = ['usuario', 'direccion', 'cupon', 'numero_orden', 'estado', 'subtotal', 'total_descuentos', 'total_impuestos', 'total']

# --- PAGO, ENTREGA Y FACTURACIÓN ---

class PagosSerializer(serializers.ModelSerializer):
    orden = serializers.PrimaryKeyRelatedField(queryset=Orden.objects.all())
    class Meta:
        model = Pagos
        fields = '__all__'

class FacturasListSerializer(serializers.ModelSerializer):
    orden = OrdenListSerializer(read_only=True)
    pago = PagosSerializer(read_only=True)
    class Meta:
        model = Facturas
        fields = '__all__'

# --- OPERATIVO ---

class MovimientosInventarioListSerializer(serializers.ModelSerializer):
    variante = VariantesArticulosListSerializer(read_only=True)
    usuario = UsuarioListSerializer(read_only=True)
    class Meta:
        model = MovimientosInventario
        fields = "__all__"