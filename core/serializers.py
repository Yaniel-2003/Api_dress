from rest_framework import serializers
from decimal import Decimal
import os, json
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

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
        fields = ['idusuario', 'email', 'nombres', 'apellidos', 'documento',
                    'numero', 'perfil', 'telefono', 'is_active','fecha_creacion']

class UsuarioWriteSerializer(serializers.ModelSerializer):
    perfil = serializers.PrimaryKeyRelatedField(queryset=Perfil.objects.all(), required=False)
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = Usuario
        fields = ['idusuario', 'email', 'nombres', 'apellidos', 'documento', 'numero', 'perfil', 'telefono', 'is_active','password']

    def validate_password(self, value):
        validate_password(value)
        return value 

    def create(self, validate_data):
        password = validate_data.pop('password', None)
        validate_data.setdefault('perfil', get_perfil_cliente())
        return Usuario.objects.create_user(password=password, **validate_data)

    def update(self, instance, validate_data):
        password = validate_data.pop('password', None)
        for attr, value in validate_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializers(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

class DireccionesListSerializer(serializers.ModelSerializer):
    usuario = UsuarioListSerializer(read_only=True)

    class Meta:
        model = Direcciones
        fields =  '__all__'

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
    historial_descuentos = serializers.SerializerMethodField()
    precio_con_descuento_activo = serializers.SerializerMethodField()

    class Meta:
        model = VariantesArticulos
        fields =  ['idvararticulo', 'articulo', 'color', 'talla', 'sku', 'stock', 'precio_extra', 'foto','precio_final', 'historial_descuentos', 'precio_con_descuento_activo']

    def get_historial_descuentos(self, obj):
        # Fetch ALL ArticuloDescuento relations for this variant
        ads = ArticuloDescuento.objects.filter(vararticulo=obj)
        historial = []
        for ad in ads:
            historial.append({
                'iddescuento': ad.descuento.iddescuento,
                'idartdescuento': ad.idartdescuento,
                'nombre': ad.descuento.nombre,
                'tipo': ad.descuento.tipo,
                'valor': ad.descuento.valor,
                'valido_desde': ad.descuento.valido_desde.date() if ad.descuento.valido_desde else None,
                'valido_hasta': ad.descuento.valido_hasta.date() if ad.descuento.valido_hasta else None,
                'cantidad_inicial': ad.cantidad_inicial,
                'cantidad_restante': ad.cantidad_restante,
                'estado': ad.descuento.estado
            })
        return historial

    def get_precio_con_descuento_activo(self, obj):
        ahora = timezone.now().date()
        ad = ArticuloDescuento.objects.filter(
            vararticulo=obj,
            descuento__valido_desde__lte=ahora,
            descuento__valido_hasta__gte=ahora,
            descuento__estado=True
        ).first()

        precio_final = obj.precio_final
        if ad:
            # Como indicaste, solo usamos porcentaje
            descuento_valor = ad.descuento.valor
            precio_con_descuento = precio_final * (Decimal('1') - Decimal(str(descuento_valor)) / Decimal('100'))
            return precio_con_descuento
        return precio_final


class variantesItemsSerializers(serializers.Serializer):
    talla = serializers.PrimaryKeyRelatedField(queryset=Tallas.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=Colores.objects.all())
    sku = serializers.CharField(required=False, allow_blank=True, default="")
    stock = serializers.IntegerField(min_value=0, default=0)
    precio_extra = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, default=0)

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

    def _leer_variantes_raw(self):
        request = self.context.get('request')
        raw = request.data.get('variantes') if request else None
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return []
        return raw if isinstance(raw, list) else []


    def _leer_fotos_validas(self):
        EXTENCIONES = ('.jpg', '.jpeg', '.png')
        request = self.context.get('request')
        if not request:
            return []
        fotos = []
        for i in range(4):
            archivos = request.FILES.get(f'foto{i}')
            if archivos and os.path.splitext(archivos.name)[1].lower() in EXTENCIONES:
                fotos.append(archivos)
        return fotos

    def to_internal_value(self, data):
        datos_mutables = {key: value for key, value in data.items()}
        if 'articulo' in data and isinstance(data['articulo'], str):
            try:
                datos_mutables['articulo'] = json.loads(data['articulo'])
            except json.JSONDecodeError:
                pass
        return super().to_internal_value(datos_mutables)
    
    
    def create(self, validated_data):
        datos_articulos = validated_data.pop('articulo')

        items = variantesItemsSerializers(data=self._leer_variantes_raw(), many=True)
        items.is_valid(raise_exception=True)
        if not items.validated_data:
            raise serializers.ValidationError({'variantes': 'Envia el menos una variante'})

        fotos = self._leer_fotos_validas()

        with transaction.atomic():
            articulo = Articulos.objects.create(**validated_data)
            variantes = [
                VariantesArticulos.objects.create(articulo=articulo, **item)
                for item in items.validated_data
            ]  

        for variante in variantes:
            for idx, archivo in enumerate(fotos):
                archivo.seek(0)
                if idx == 0 and not variante.foto:
                    variante.foto = archivo
                    archivo.save(update_fields=['foto'])
                    archivo.seek(0)
                FotoVarianteArticulo.objects.create(
                    variante_articulo = variante,
                    archivo = archivo
                )
        return variante[0]
        
    def update(self, instance, validated_data):
        datos_articulo = validated_data.pop('articulo', None)
        fotos = self._leer_fotos_validas()

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if datos_articulo:
                articulo = instance.articulo
                for attr, value in datos_articulo.items():
                    setattr(self.articulo, attr, value)
                articulo.save()

            fotos_viejas = list(instance.fotovariantearticulo_set.all()) if fotos else []

        if fotos:
            for f in fotos_viejas:
                f.archivo.delete(save=False)
                f.delete()
            for idx, archivo in enumerate(fotos):
                archivo.seek(0)
                if idx == 0:
                    instance.foto = archivo
                    archivo.save(update_fields=['foto'])
                    archivo.seek(0)
                FotoVarianteArticulo.objects.create(
                    variante_articulo = instance,
                    archivo = archivo
                )
        return instance


class ArticuloDescuentoSerializer(serializers.ModelSerializer):
    descuento = DescuentosSerializer(read_only=True)
    precio_con_descuento = serializers.ReadOnlyField(source='precio_calculado')

    class Meta:
        model = ArticuloDescuento
        fields = ['idartdescuento', 'vararticulo', 'descuento', 'precio_con_descuento','cantidad_inicial', 'cantidad_restante']



class ArticuloDescuentoWriteSerializer(serializers.ModelSerializer):
    vararticulo = serializers.PrimaryKeyRelatedField(queryset=VariantesArticulos.objects.all(), required=False)
    vararticulos = serializers.PrimaryKeyRelatedField(queryset=VariantesArticulos.objects.all(), many=True, required=False, write_only=True)
    descuento = DescuentosSerializer()

    class Meta:
        model = ArticuloDescuento
        fields = ['idartdescuento', 'vararticulo', 'vararticulos', 'descuento', 'cantidad_inicial', 'cantidad_restante']

    def create(self, validated_data):
        # Sacamos el diccionario anidado que llega desde React
        datos_descuento = validated_data.pop('descuento')

        lista_variantes = validated_data.pop('vararticulos', [])
        variantes_individual = validated_data.pop('vararticulo', None)

        with transaction.atomic():
            # Creamos el Descuento
            nuevo_descuento = Descuentos.objects.create(**datos_descuento)

            if lista_variantes:
                articulos_creados = []
                for variante in lista_variantes:
                    añadir = ArticuloDescuento.objects.create(
                        descuento = nuevo_descuento,
                        vararticulo = variante,
                        **validated_data
                    )
                    articulos_creados.append(añadir)
                return articulos_creados[0]

            # Creamos la tabla intermedia con el nuevo descuento
            elif variantes_individual:
                añadir = ArticuloDescuento.objects.create(
                    descuento = nuevo_descuento,
                    vararticulo = variantes_individual,
                    **validated_data
                )
                return añadir

    def update(self, instance, validated_data):
        datos_descuento = validated_data.pop('descuento', None)
        
        with transaction.atomic():
            # Actualizamos la tabla intermedia
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Actualizamos el descuento anidado
            if datos_descuento:
                descuento_instancia = instance.descuento
                for attr, value in datos_descuento.items():
                    setattr(descuento_instancia, attr, value)
                descuento_instancia.save()
                
            return instance


#### ENDPOINTS PARA LA VISTA PRINCIPAL
class VarianteArticulosSerializers(serializers.ModelSerializer):
    tallas_nombre = serializers.CharField(source='talla.codigo', read_only=True)
    regla_tallaje = serializers.CharField(source='talla.regla_tallaje', read_only=True)
    tipo_regla_tallaje = serializers.CharField(source='talla.tipo', read_only=True)
    color_nombre = serializers.CharField(source='color.nombre', read_only=True)
    articulos_nombre = serializers.CharField(source='articulo.nombre', read_only=True)
    descripcion = serializers.CharField(source='articulo.descripcion', read_only=True)
    descuentos_activos = serializers.SerializerMethodField()
    class Meta:
        model = VariantesArticulos
        fields = [
            'idvararticulo',
            'regla_tallaje',
            'descripcion',
            'tallas_nombre',
            'tipo_regla_tallaje',
            'color_nombre',
            'articulos_nombre',
            'stock',
            'precio_extra',
            'foto',
            'precio_final',
            'descuentos_activos'
        ]

    def get_descuentos_activos(self, obj):
        descuentos_filtrados = obj.articulodescuento_set.filter(descuento__estado=True)

        return ArticuloDescuentoSerializer(descuentos_filtrados, many=True, context=self.context).data

        



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