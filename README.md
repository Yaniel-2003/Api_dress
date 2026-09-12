# Dress Shopy — API

Backend de **Dress Shopy**, una tienda de ropa online. Construido con **Django 6** y **Django REST Framework**, expone una API REST protegida con **JWT** para gestionar catálogo de productos, variantes (talla/color), usuarios, direcciones, descuentos y cupones sobre una base de datos **SQL Server**.

> Este backend está pensado para consumirse desde el front-end en React/Vite del mismo proyecto (`../front-end`).

---

## Tabla de contenido

- [Stack técnico](#stack-técnico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelo de datos](#modelo-de-datos)
- [Requisitos previos](#requisitos-previos)
- [Instalación y puesta en marcha](#instalación-y-puesta-en-marcha)
- [Variables de entorno](#variables-de-entorno)
- [Autenticación (JWT)](#autenticación-jwt)
- [Endpoints de la API](#endpoints-de-la-api)
- [Archivos de media](#archivos-de-media)
- [Panel de administración](#panel-de-administración)
- [Notas y puntos a mejorar](#notas-y-puntos-a-mejorar)

---

## Stack técnico

| Componente | Tecnología |
|---|---|
| Framework | Django 6.0.6 |
| API | Django REST Framework 3.17 |
| Autenticación | `djangorestframework_simplejwt` 5.5 (JWT) |
| Base de datos | SQL Server (vía `mssql-django` + `pyodbc`) |
| CORS | `django-cors-headers` |
| Panel admin | `django-jazzmin` (tema visual para el admin de Django) |
| Configuración | `python-dotenv` (variables en `.env`) |

Dependencias completas en [`requirements.txt`](./requirements.txt).

## Estructura del proyecto

```
api/
├── manage.py
├── requirements.txt
├── .env                        # variables de entorno (NO se sube a git)
├── config/                     # configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py                 # monta /admin/ y /api/
│   ├── asgi.py / wsgi.py
├── core/                       # única app Django del proyecto
│   ├── models.py                # todo el modelo de datos (ver más abajo)
│   ├── serializers.py
│   ├── admin.py                  # registro de modelos en el admin (Jazzmin)
│   ├── paginacion.py             # paginación global de la API
│   ├── migrations/
│   ├── urls/                     # urls separadas por dominio
│   │   ├── __init__.py           # agrupa todos los sub-urls bajo /api/
│   │   ├── auth_urls.py          # /api/login/, /api/logout/
│   │   ├── usuarios_urls.py      # /api/usuario/
│   │   ├── direcciones_urls.py   # /api/direcciones/
│   │   ├── catalogo_urls.py      # marca, color, talla, categoría, cupón, etc.
│   │   └── articulo_urls.py      # /api/articulos/, variantes, fotos, descuentos
│   └── views/                    # vistas separadas por dominio (mismo criterio que urls/)
│       ├── auth_views.py
│       ├── usuarios_views.py
│       ├── direcciones_views.py
│       ├── catalogo.py
│       └── articulos_views.py
└── _migraciones_backup/        # histórico de migraciones anteriores (no se usa en runtime)
```

> Nota: `_migraciones_backup/`, `backup_core_utf8.json` y `_usuarios_old_raw.json` parecen respaldos de una migración/reset de base de datos anterior. No forman parte del flujo normal de la app.

## Modelo de datos

Todas las tablas viven en la app `core` (`core/models.py`) y usan **UUID como llave primaria**. Se agrupan así:

- **Catálogo base**: `Genero`, `NunDocumento`, `Perfil`, `Marcas`, `Colores`, `Cat_Reglas_Tallaje`, `Prendas`, `Tallas`, `Impuestos`, `Descuentos`, `Cupones`, `Categoria`.
- **Usuarios y direcciones**: `Usuario` (modelo de usuario personalizado, login por `email`), `Direcciones`.
- **Productos**: `Articulos` (producto base), `VariantesArticulos` (SKU por talla/color, con stock y foto), `FotoVarianteArticulo` (fotos adicionales), `ArticuloDescuento` (descuentos aplicados a una variante).
- **Carrito**: `Carrito`, `ItemsCarrito`.
- **Órdenes y pagos**: `Orden`, `ItemsOrden`, `Pagos`, `Entregas`, `Facturas`.
- **Soporte operativo**: `Devoluciones`, `MovimientosInventario`, `Notificaciones`.

Detalles relevantes:

- `Usuario` extiende `AbstractBaseUser` + `PermissionsMixin`, usa `email` como `USERNAME_FIELD` y está configurado como `AUTH_USER_MODEL = 'core.Usuario'`.
- `Articulos.precio_con_impuesto` y `VariantesArticulos.precio_final` calculan el precio con impuesto incluido a partir del precio base + precio extra de la variante.
- `ArticuloDescuento.precio_calculado` valida vigencia (`valido_desde`/`valido_hasta`) y cantidad restante antes de aplicar el descuento (porcentaje o valor fijo) sobre `precio_final`.
- Todas las tablas mapean a nombres `SH_*` en la base de datos (`db_table`), pensado para una base SQL Server ya existente/compartida.

## Requisitos previos

- **Python 3.11+** (probado con 3.14).
- **SQL Server** accesible (local o remoto) con la base de datos creada.
- **ODBC Driver 17 for SQL Server** instalado en el sistema (requerido por `pyodbc`/`mssql-django`).
- `pip` para instalar dependencias.

## Instalación y puesta en marcha

```bash
# 1. Entrar a la carpeta del backend
cd api

# 2. Crear y activar entorno virtual
python -m venv venvDS
venvDS\Scripts\activate        # Windows
# source venvDS/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear el archivo .env (ver sección de variables de entorno)
copy .env.example .env         # si no existe, créalo manualmente con los valores de abajo

# 5. Aplicar migraciones sobre la base de datos configurada
python manage.py migrate

# 6. Crear un superusuario para entrar al panel de administración
python manage.py createsuperuser

# 7. Levantar el servidor de desarrollo
python manage.py runserver
```

Por defecto el servidor queda disponible en `http://127.0.0.1:8000/`, y la API bajo `http://127.0.0.1:8000/api/`.

## Variables de entorno

El archivo `.env` se carga desde `config/settings.py` con `python-dotenv`. Variables usadas:

| Variable | Descripción | Valor por defecto en el código |
|---|---|---|
| `DEBUG` | Modo debug de Django | `True` (hardcodeado en `settings.py`, el valor del `.env` no se lee actualmente) |
| `SECRET_KEY` | Clave secreta de Django | *(no se lee del `.env` todavía, ver [Notas](#notas-y-puntos-a-mejorar))* |
| `DB_ENGINE` | Motor de base de datos | `mssql` |
| `DB_NAME` | Nombre de la base de datos | `shopy_dress` |
| `DB_USER` | Usuario de SQL Server | `sa` |
| `DB_PASSWORD` | Contraseña de SQL Server | — |
| `DB_HOST` | Host de SQL Server | `127.0.0.1` |
| `DB_PORT` | Puerto de SQL Server | `1433` |

Ejemplo de `.env`:

```env
DEBUG=True
SECRET_KEY=cambia-esta-clave-por-una-segura

DB_ENGINE=mssql
DB_NAME=shopy_dress
DB_USER=sa
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=1433
```

`CORS_ALLOWED_ORIGINS` está fijado en `settings.py` a `http://localhost:5173` y `http://127.0.0.1:5173` (el puerto por defecto de Vite). Si el front corre en otro host/puerto, hay que actualizarlo ahí.

## Autenticación (JWT)

La API usa `rest_framework_simplejwt` como único backend de autenticación (`DEFAULT_AUTHENTICATION_CLASSES`).

- **Login**: `POST /api/login/` con `{ "email": "...", "password": "..." }` → responde `access`, `refresh` y los datos del `usuario`.
- **Uso del token**: enviar `Authorization: Bearer <access>` en cada request a un endpoint protegido.
- **Logout**: `POST /api/logout/` (requiere estar autenticado) con `{ "refresh": "..." }`.
- **Duración**: access token 1 día, refresh token 7 días (`SIMPLE_JWT` en `settings.py`).
- El claim de usuario usa `idusuario` (UUID) en vez del `id` numérico por defecto de Django (`USER_ID_FIELD` / `USER_ID_CLAIM`).

> El registro de usuarios se hace por el endpoint estándar `POST /api/usuario/` (ver tabla de endpoints), que es público.

## Endpoints de la API

Todos los endpoints cuelgan del prefijo `/api/`.

### Autenticación

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| POST | `/api/login/` | Público | Inicia sesión y devuelve tokens JWT |
| POST | `/api/logout/` | Autenticado | Invalida (recibe) el refresh token |

### Usuarios

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/usuario/` | Autenticado | Lista usuarios (filtro `?buscar=`, `?documento=`, `?nombre=`) |
| POST | `/api/usuario/` | Público | Registro de nuevo usuario |
| GET/PUT/PATCH/DELETE | `/api/usuario/{id}/` | Autenticado | Detalle / actualización / borrado |

### Direcciones

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET/POST | `/api/direcciones/` | Público (`AllowAny`) | Listar / crear direcciones (filtro `?buscar=`) |
| GET/PUT/PATCH/DELETE | `/api/direcciones/{id}/` | Público (`AllowAny`) | Detalle / actualización / borrado |

### Catálogo (CRUD estándar vía router)

| Recurso | Ruta base | Permiso |
|---|---|---|
| Género | `/api/genero/` | Autenticado |
| Tipo de documento | `/api/tipo-numero-documento/` | Autenticado |
| Perfil | `/api/perfil/` | Autenticado |
| Marca | `/api/marca/` | Autenticado |
| Color | `/api/color/` | Autenticado |
| Talla | `/api/talla/` | Autenticado |
| Impuesto | `/api/impuesto/` | Autenticado |
| Descuento | `/api/descuento/` | Autenticado |
| Cupón | `/api/cupon/` | Autenticado |
| Categoría | `/api/categoria/` | Autenticado |
| Prendas | `/api/prendas/` | Autenticado |

### Artículos y variantes

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET/POST | `/api/articulos/` | Autenticado | Listar/crear artículos (filtros `?buscar=`, `?marca=`, `?categoria=`, `?estado=`) |
| GET/PUT/PATCH/DELETE | `/api/articulos/{id}/` | Autenticado | Detalle / actualización / borrado |
| GET/POST | `/api/variantes-articulos/` | Autenticado | Listar/crear variantes (filtros `?buscar=`, `?color=`, `?talla=`, `?marca=`, `?categoria=`, `?prendas=`, `?estado=`, admite listas separadas por coma) |
| GET/PUT/PATCH/DELETE | `/api/variantes-articulos/{id}/` | Autenticado | Detalle / actualización / borrado |
| GET | `/api/variantes-articulos/tienda_publica/` | **Público** | Vitrina pública: solo variantes con `stock > 0` y artículo activo, con descuentos precargados |
| GET | `/api/variantes/{idvararticulo}/fotos/` | Autenticado | Lista las fotos de una variante |
| GET/POST | `/api/descuento-articulos/` | Autenticado | Listar/crear descuentos aplicados a variantes |
| GET/PUT/PATCH/DELETE | `/api/descuento-articulos/{id}/` | Autenticado | Detalle / actualización / borrado |

Todos los listados (excepto los que declaran su propia paginación) usan `PaginacionGlobal`: 50 resultados por página, máximo 100.

## Archivos de media

Las fotos de las variantes de producto (`VariantesArticulos.foto`, `FotoVarianteArticulo.archivo`) se guardan en disco bajo `Fotos_articulos/Articulo<uuid>/...`, fuera de la carpeta `api/` (en la raíz del repositorio). Se sirven en desarrollo (`DEBUG=True`) desde `MEDIA_URL = /media/`.

## Panel de administración

Disponible en `/admin/` con el tema **Jazzmin**. Ahí se gestionan directamente los catálogos (género, marca, color, talla, impuesto, descuento, cupón, categoría, prenda, permisos) y los usuarios (`UsuarioAdmin`, con búsqueda por email/nombre/apellidos/número y filtros por estado/perfil). El campo `password` es de solo lectura en el admin: se gestiona vía registro o `manage.py changepassword`.

## Notas y puntos a mejorar

Cosas detectadas al revisar el código que vale la pena tener en cuenta antes de llevar esto a producción:

- **Secretos hardcodeados**: `settings.py` trae un `SECRET_KEY` de ejemplo y una contraseña de base de datos por defecto escritos directamente en el código (como *fallback* de `os.environ.get(...)`). Aunque el `.env` real está en `.gitignore`, estos valores por defecto sí quedan en el historial del repo. Se recomienda no dejar contraseñas reales como fallback y rotar esa `SECRET_KEY`/contraseña si ya se compartió el repo.
- **`MEDIA_ROOT` con ruta absoluta de Windows**: apunta a `C:\Users\PC\...`, lo que hace el proyecto no portable a otras máquinas/SO. Conviene definirlo relativo a `BASE_DIR`.
- **`/api/direcciones/` es público** (`AllowAny`), a diferencia del resto de recursos que exigen JWT. Revisar si es intencional o debería requerir autenticación.
- **Subida de fotos deshabilitada**: el método `POST` de `Fotos_articulos` (subir fotos de una variante) está comentado en `core/views/articulos_views.py`; hoy el endpoint solo permite `GET`.
- **Typo en paginación**: `PaginacionGlobal.pague_size_query_param` (en `core/paginacion.py`) debería llamarse `page_size_query_param`; tal como está, DRF no lo reconoce y el tamaño de página no se puede sobreescribir por query param.
- `DEBUG` y `SECRET_KEY` están definidos en `.env` pero **no se leen** desde `settings.py` (siguen hardcodeados); si se quiere que el `.env` controle esto, hay que cablearlo en `settings.py`.
