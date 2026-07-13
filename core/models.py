import uuid
from django.db import models

#### TABLAS CATALOGO 

class Genero(models.Model):
    idgenero = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Genero'
        managed = True

    def __str__(self):
        return f"{self.nombre}"


class NunDocumento(models.Model):
    idnumero = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sigla = models.CharField(max_length=5, null=True, blank=True)
    nombre = models.CharField(max_length=40)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Tipo_Documento'
        managed = True


class Perfil(models.Model):
    idperfil = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50, unique=True) # Ej: 'Administrador', 'Cliente', 'Vendedor'
    descripcion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Perfil'
        managed = True

    def __str__(self):
        return self.nombre


class Marcas(models.Model):
    idmarca = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Marca'
        managed = True
    
    def __str__(self):
        return f"{self.nombre}"
    

class Colores(models.Model): 
    idcolor = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50, null=True, blank=True)
    hex_code = models.CharField(max_length=7, null=True, blank=True)

    class Meta:
        db_table = 'SH_Color'
        managed = True

    def __str__(self):
        return f"{self.nombre} - {self.hex_code}"    


class Tallas(models.Model):
    idtalla = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=10, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'SH_Talla'
        managed = True

    def __str__(self):
        return f"{self.codigo} ({self.tipo})"


class Impuestos(models.Model):
    idimpuesto = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=80)
    porcentaje = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Impuesto'
        managed = True

    def __str__(self):
        return f"{self.nombre} - {self.porcentaje}%"
    

class Descuentos(models.Model):
    iddescuento = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    valido_desde = models.DateTimeField()
    valido_hasta = models.DateTimeField()
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Descuento'
        managed = True

    def __str__(self):
        return f"{self.nombre} - {self.valor} ({self.tipo})"
    

class Cupones(models.Model):
    idcupon = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=30, unique=True)
    tipo = models.CharField(max_length=15)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    uso_maximo = models.PositiveIntegerField()
    uso_por_usuario = models.PositiveIntegerField()
    usos_actuales = models.PositiveIntegerField(default=0)
    valido_desde = models.DateTimeField()
    valido_hasta = models.DateTimeField()
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'SH_Cupon'
        managed = True

    def __str__(self):
        return f"{self.codigo}"
    


#### CATEGORÍAS 

class Categoria(models.Model):
    idcategoria = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    genero = models.ForeignKey("Genero", on_delete=models.PROTECT)
    padre = models.ForeignKey("Categoria", on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Categoria'
        managed = True

    def __str__(self):
        return f"{self.nombre}"
    


#### USUARIOS Y DIRECCIONES 
### ESTA FUNCION ENVIA UN PERFIL (CLIENTE) POR DEFECTO CUANDO SE REINICIE 

def get_perfil_cliente():
    perfil, creado = Perfil.objects.get_or_create(nombre='cliente');
    return perfil.idperfil

### ACTUALIZAMOS EL CAMPO DE USUARIO

class Usuario(models.Model):
    idusuario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    documento = models.ForeignKey('NunDocumento', on_delete=models.CASCADE)
    ## AGREGAMOS LA FUNCION get_perfil_cliente
    perfil = models.ForeignKey('Perfil', on_delete=models.PROTECT, default=get_perfil_cliente)
    email = models.EmailField(max_length=254, unique=True)
    password_hash = models.CharField(max_length=255)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "SH_Usuarios"
        managed = True

    def __str__(self):
        return f"{self.email}"
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_active(self):
        return self.activo
    
    @property
    def is_staff(self):
        return self.perfil.nombre.lower() == 'Administrador'
    

class Direcciones(models.Model):
    iddireccion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    nombre_destinatario = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    residencia = models.CharField(max_length=200)
    barrio = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=15)
    principal = models.BooleanField(default=True)

    class Meta:
        db_table = 'SH_Direccion'
        managed = True

    def __str__(self):
        return f"{self.nombre_destinatario} - {self.direccion}"
    


#### CATÁLOGO DE PRODUCTOS 

class Articulos(models.Model):
    idarticulo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    marca = models.ForeignKey('Marcas', on_delete=models.CASCADE)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    impuestos = models.ForeignKey('Impuestos', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    slug = models.CharField(max_length=220, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    precio_base = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'SH_Articulo'
        managed = True 

    def __str__(self):
        return f"{self.nombre}"


class VariantesArticulos(models.Model):
    idvararticulo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    articulo = models.ForeignKey('Articulos', on_delete=models.CASCADE)
    color = models.ForeignKey('Colores', on_delete=models.CASCADE)
    talla = models.ForeignKey('Tallas', on_delete=models.CASCADE)
    sku = models.CharField(max_length=60, unique=True)
    stock = models.IntegerField()
    precio_extra = models.DecimalField(max_digits=10, decimal_places=2)
    foto = models.CharField(max_length=1000)

    class Meta:
        db_table = 'SH_Variante_Articulos'
        managed = True

    def __str__(self):
        return f"SKU: {self.sku} - Stock: {self.stock}"
    

class ArticuloDescuento(models.Model):
    idartdescuento = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vararticulo = models.ForeignKey('VariantesArticulos', on_delete=models.CASCADE)
    descuento = models.ForeignKey('Descuentos', on_delete=models.CASCADE)

    class Meta:
        db_table = 'SH_Articulo_Descuento'
        managed = True
        
    def __str__(self):
        return f"Descuento para Variante: {self.vararticulo}"



#### CARRITO DE COMPRAS 

class Carrito(models.Model):
    idcarrito = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True) 

    class Meta:
        db_table = 'SH_Carrito'
        managed = True
        
    def __str__(self):
        return f"Carrito de: {self.usuario}"


class ItemsCarrito(models.Model):
    iditmcarrito = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE)
    vararticulo = models.ForeignKey('VariantesArticulos', on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    class Meta:
        db_table = 'SH_Items_Carrito'
        managed = True
        
    def __str__(self):
        return f"{self.cantidad}x de Variante: {self.vararticulo}"



#### ÓRDENES DE COMPRA 

class Orden(models.Model):
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('enviada', 'Enviada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]

    idorden = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    direccion = models.ForeignKey('Direcciones', on_delete=models.CASCADE)
    cupon = models.ForeignKey('Cupones', on_delete=models.SET_NULL, null=True, blank=True)
    numero_orden = models.CharField(max_length=30, unique=True)
    estado = models.CharField(max_length=30, choices=ESTADOS_CHOICES, default='pendiente')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    total_descuentos = models.DecimalField(max_digits=12, decimal_places=2)
    total_impuestos = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'SH_Orden'
        managed = True
        
    def __str__(self):
        return f"Orden {self.numero_orden} - {self.estado}"


class ItemsOrden(models.Model):
    iditmorden = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE)
    vararticulo = models.ForeignKey('VariantesArticulos', on_delete=models.SET_NULL, null=True, blank=True)
    descuento = models.ForeignKey('Descuentos', on_delete=models.SET_NULL, null=True, blank=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    descuento_aplicado = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'SH_Items_Compra'
        managed = True
        
    def __str__(self):
        return f"{self.cantidad}x de {self.vararticulo} en {self.orden}"



#### PAGO, ENTREGA Y FACTURACIÓN

class Pagos(models.Model):
    idpago = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE)
    metodo = models.CharField(max_length=30)
    referencia_externa = models.CharField(max_length=100, null=True, blank=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20)
    fecha_pago = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'SH_Pagos'
        managed = True

    def __str__(self):
        return f"Pago {self.idpago} - {self.estado}"


class Entregas(models.Model):
    identrega = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE)
    transportadora = models.CharField(max_length=100)
    numero_guia = models.CharField(max_length=100)
    estado = models.CharField(max_length=30)
    fecha_estimada = models.DateTimeField()
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'SH_Entrega'
        managed = True

    def __str__(self):
        return f"Guía {self.numero_guia} - {self.estado}"


class Facturas(models.Model):
    idfactura = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE)
    pago = models.ForeignKey('Pagos', on_delete=models.CASCADE)
    numero_factura = models.CharField(max_length=30, unique=True)
    base_gravable = models.DecimalField(max_digits=12, decimal_places=2)
    monto_impuesto = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20)
    numero_resolucion_dian = models.CharField(max_length=50)
    prefijo_factura = models.CharField(max_length=10)
    cufe = models.CharField(max_length=200)
    qr_url = models.CharField(max_length=500)
    ambiente = models.CharField(max_length=15)
    emitida_en = models.DateTimeField()

    class Meta:
        db_table = 'SH_Factura'
        managed = True

    def __str__(self):
        return f"{self.numero_factura} - Total: {self.total}"


#### DEVOLUCIONES, AUDITORÍA Y ALERTAS (Soporte Operativo)

class Devoluciones(models.Model):
    iddevolucion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE)
    item_orden = models.ForeignKey('ItemsOrden', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    motivo = models.TextField()
    estado = models.CharField(max_length=20)
    monto_reembolso = models.DecimalField(max_digits=12, decimal_places=2)
    tipo_reembolso = models.CharField(max_length=20)
    creado_en = models.DateTimeField(auto_now_add=True)
    resuelto_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'SH_Devolucion'
        managed = True

    def __str__(self):
        return f"Devolución {self.iddevolucion} - Estado: {self.estado}"


class MovimientosInventario(models.Model):
    idmovinventario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variante = models.ForeignKey('VariantesArticulos', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15)
    cantidad = models.PositiveIntegerField()  
    stock_anterior = models.IntegerField()
    stock_resultante = models.IntegerField()
    motivo = models.CharField(max_length=200)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'SH_Movimiento_Inventario'
        managed = True

    def __str__(self):
        return f"{self.tipo.upper()} - {self.cantidad} unds"


class Notificaciones(models.Model):
    idnotificacion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30)
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False) 
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'SH_Notificacion'
        managed = True

    def __str__(self):
        return f"{self.titulo}"