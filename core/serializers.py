from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from decimal import Decimal
import os, json
from django.db import transaction
from django.utils import timezone
import json
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

class CatReglasTallajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat_Reglas_Tallaje
        fields = "__all__"

class PrendasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prendas
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
                "id": obj.padre.idcategoria,
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
    prendas = PrendasSerializer(read_only=True)

    class Meta:
        model = Articulos
        fields = ['idarticulo', 'marca', 'categoria', 'impuestos', 'prendas', 'nombre', 'slug', 'descripcion', 'precio_base', 'estado', 'precio_con_impuesto']
    

class ArticulosWriteSerializer(serializers.ModelSerializer):
    marca = serializers.PrimaryKeyRelatedField(queryset=Marcas.objects.all())
    categoria = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())
    impuestos = serializers.PrimaryKeyRelatedField(queryset=Impuestos.objects.all())
    prendas = serializers.PrimaryKeyRelatedField(queryset=Prendas.objects.all())

    class Meta:
        model = Articulos
        #LA AGREGAMOS EN LAS FILAS DE LA TABLA
        fields = ['idarticulo', 'marca', 'categoria', 'impuestos', 'prendas', 'nombre', 'slug', 'descripcion', 'precio_base', 'estado', 'precio_con_impuesto']
        extra_kwargs = {
            'slug': {'validators': []},
        }

class VariantesArticulosListSerializer(serializers.ModelSerializer):
    articulo = ArticulosListSerializer(read_only=True)
    color = ColoresSerializer(read_only=True)
    talla = TallasSerializer(read_only=True)

    class Meta:
        model = VariantesArticulos
        fields =  ['idvararticulo', 'articulo', 'color', 'talla', 'sku', 'stock', 'precio_extra', 'foto','precio_final']

class VariantesArticulosWriteSerializer(serializers.ModelSerializer):
    articulo = ArticulosWriteSerializer()
    color = serializers.PrimaryKeyRelatedField(queryset=Colores.objects.all(), required=False, allow_null=True)
    talla = serializers.PrimaryKeyRelatedField(queryset=Tallas.objects.all(), required=False, allow_null=True)

    sku = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    stock = serializers.IntegerField(required=False, allow_null=True)
    precio_extra = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)

    

    class Meta:
        model = VariantesArticulos
        fields = ['idvararticulo', 'articulo', 'color', 'talla', 'sku', 'stock', 'precio_extra', 'foto','precio_final']

    def to_internal_value(self, data):
        datos_mutables = {key: value for key, value in data.items()}
        if 'articulo' in data and isinstance(data['articulo'], str):
            try:
                datos_mutables['articulo'] = json.loads(data['articulo'])
            except json.JSONDecodeError:
                pass
        return super().to_internal_value(datos_mutables)
    
    
    def create(self, validated_data):
        EXTENSIONES = ['.jpg', '.png', '.jpeg']
        datos_articulo = validated_data.pop('articulo')

        request = self.context.get('request')
        variante_raw = request.data.get('variantes') if request else None

        if isinstance(variante_raw, str):
            try:
                variante_list = json.loads(variante_raw)
            except json.JSONDecodeError:
                variante_list = []
        elif isinstance(variante_raw, list):
            variante_list = variante_raw
        else:
            variante_list = []


        with transaction.atomic():
            slug_articulo = datos_articulo.get('slug')
            if slug_articulo:
                nuevos_articulos, _ = Articulos.objects.get_or_create(
                    slug=slug_articulo,
                    defaults=datos_articulo
                )
            else:
                nuevos_articulos = Articulos.objects.create(**datos_articulo)

            primer_variante = None

            for var_data in variante_list:
                sku_val = str(var_data.get('sku', '')).strip()
                color_id = var_data.get('color')
                talla_id = var_data.get('talla')

                try:
                    stock_val = int(var_data.get('stock')) if var_data.get('stock') not in (None, '') else 0
                except (ValueError, TypeError):
                    stock_val = 0

                try:
                    precio_extra_val = Decimal(str(var_data.get('precio_extra'))).quantize(Decimal('0.01')) if var_data.get('precio_extra') not in (None, '') else Decimal('0.00')
                except Exception:
                    precio_extra_val = Decimal('0.00')

                if sku_val:
                    variante, _ = VariantesArticulos.objects.update_or_create(
                        sku=sku_val,
                        defaults={
                            'articulo': nuevos_articulos,
                            'color_id': color_id,
                            'talla_id': talla_id,
                            'stock': stock_val,
                            'precio_extra': precio_extra_val,
                        }
                    )
                else:
                    variante = VariantesArticulos.objects.create(
                        articulo=nuevos_articulos,
                        color_id=color_id,
                        talla_id=talla_id,
                        sku='',
                        stock=stock_val,
                        precio_extra=precio_extra_val,
                    )

                if not primer_variante:
                    primer_variante = variante

                if request:
                    for i in range(4):
                        archivo = request.FILES.get(f'foto{i}')

                        if not archivo: continue

                        ext = os.path.splitext(archivo.name)[1].lower()

                        if ext not in EXTENSIONES:
                            continue
                        
                        if not variante.foto:
                            variante.foto = archivo
                            variante.save()

                        foto = FotoVarianteArticulo(variante_articulo=variante)
                        foto.archivo.save(archivo.name, archivo, save=True)

            return primer_variante or nuevos_articulos
        
    def update(self, instance, validated_data):
        EXTENSIONES = ['.jpg', '.png', '.jpeg']
        datos_articulo = validated_data.pop('articulo', None)

        with transaction.atomic():
            #ACTUALIZAR LOS CAMPOS DE LA VARIANTE
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            variante = instance
            # SI SE ENVIARON DATOS LOS ACTUALIZAMOS
            if datos_articulo:
                articulo_existente = instance.articulo #ACCEDEMOS AL ARTICULO
                for attr, value in datos_articulo.items(): #RECORREMOS LOS DATOS NUEVOS
                    setattr(articulo_existente, attr, value) # MODIFICAMS LOS CAMPOS
                articulo_existente.save()

            request = self.context.get('request')

            errores = []

            # ACTUALIZA LAS FOTOS Y ELIMINA LAS ANTIGUAS
            FotoVarianteArticulo.objects.filter(variante_articulo=variante).delete()

            for i in range (4):
                archivo = request.FILES.get(f'foto{i}')

                if not archivo: continue

                ext = os.path.splitext(archivo.name)[1].lower()

                if ext not in EXTENSIONES:
                    errores.append(f"Foto{i}: extension no permitida") 
                    continue
                
                if not variante.foto:
                    variante.foto = archivo
                    variante.save()

                
                nueva_foto = FotoVarianteArticulo(variante_articulo=variante)
                nueva_foto.archivo.save(archivo.name, archivo, save=True)

            return instance

class ArticuloDescuentoSerializer(serializers.ModelSerializer):
    vararticulo = VariantesArticulosListSerializer(read_only=True)
    descuento = DescuentosSerializer(read_only=True)
    precio_con_descuento = serializers.SerializerMethodField()

    class Meta:
        model = ArticuloDescuento
        fields = ['idartdescuento', 'vararticulo', 'descuento', 'precio_con_descuento','cantidad_inicial', 'cantidad_restante']

    def get_precio_con_descuento(self, articuloDescuento):
        precio_final = articuloDescuento.vararticulo.precio_final
        descuento = articuloDescuento.descuento.valor

        cantidad_restante = articuloDescuento.cantidad_restante
        precio_con_descuento = precio_final * (Decimal('1')- Decimal(str(descuento)) / Decimal(100))


        fecha1 = articuloDescuento.descuento.valido_desde 
        fecha2 = articuloDescuento.descuento.valido_hasta 

        ahora = timezone.now().date()


        if (ahora < fecha1 or ahora > fecha2) or cantidad_restante <= 0:
            return precio_final
            
        return precio_con_descuento
            
        



        



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