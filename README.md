# Dress Shopy — API

Backend de **Dress Shopy**, una tienda de ropa online. Construido con **Django 6** y **Django REST Framework**, expone una API REST protegida con **JWT** para gestionar catálogo de productos, variantes (talla/color), usuarios, direcciones, descuentos, cupones y carrito de compras sobre una base de datos **SQL Server**.

> Este backend se consume desde el front-end en React/Vite del repositorio hermano [`Frontend-Dress`](https://github.com/Yaniel-2003/Frontend-Dress).

---

## Tabla de contenido

- [Stack técnico](#stack-técnico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelo de datos](#modelo-de-datos)
- [Requisitos previos](#requisitos-previos)
- [Instalación y puesta en marcha (Ubuntu)](#instalación-y-puesta-en-marcha-ubuntu)
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
| Imágenes | `pillow` |
| Configuración | `python-dotenv` (variables en `.env`) |

Dependencias completas en [`requirements.txt`](./requirements.txt).

## Estructura del proyecto

```
Api_dress/
├── manage.py
├── requirements.txt
├── update_rules.py             # script puntual para reasignar reglas de tallaje a prendas/tallas
├── .env                        # variables de entorno (NO se sube a git)
├── config/                     # configuración del proyecto Django
│   ├── settings.py
│   ├── urls.py                 # monta /admin/ y /api/
│   └── asgi.py / wsgi.py
└── core/                       # única app Django del proyecto
    ├── models.py               # todo el modelo de datos (ver más abajo)
    ├── serializers.py
    ├── admin.py                # registro de modelos en el admin (Jazzmin)
    ├── paginacion.py           # paginación global de la API
    ├── send_email.py           # correo de recuperación de contraseña
    ├── migrations/
    ├── urls/                   # urls separadas por dominio
    │   ├── __init__.py         # agrupa todos los sub-urls bajo /api/
    │   ├── auth_urls.py        # login, logout, token, recuperación de contraseña
    │   ├── usuarios_urls.py    # /api/usuario/
    │   ├── direcciones_urls.py # /api/direcciones/
    │   ├── catalogo_urls.py    # marca, color, talla, categoría, cupón, etc.
    │   ├── articulo_urls.py    # /api/articulos/, variantes, fotos, descuentos
    │   └── carrito_urls.py     # /api/carritos-compras/, agregar_item_carrito
    └── views/                  # vistas separadas por dominio (mismo criterio que urls/)
        ├── auth_views.py
        ├── usuarios_views.py
        ├── direcciones_views.py
        ├── catalogo.py
        ├── articulos_views.py
        └── carrito_views.py
```

> `_migraciones_backup/`, `backup_core_utf8.json` y `_usuarios_old_raw.json` son respaldos locales de un reset anterior de la base de datos. Están en el `.gitignore`, no se suben al repositorio y no forman parte del flujo normal de la app.

## Modelo de datos

Todas las tablas viven en la app `core` (`core/models.py`) y usan **UUID como llave primaria**. Se agrupan así:

- **Catálogo base**: `Genero`, `NunDocumento`, `Perfil`, `Marcas`, `Colores`, `Cat_Reglas_Tallaje`, `Prendas`, `Tallas`, `Impuestos`, `Descuentos`, `Cupones`, `Categoria`.
- **Usuarios y direcciones**: `Usuario` (modelo de usuario personalizado, login por `email`), `Direcciones`.
- **Productos**: `Articulos` (producto base), `VariantesArticulos` (SKU por talla/color, con stock y foto), `FotoVarianteArticulo` (fotos adicionales), `ArticuloDescuento` (descuentos aplicados a una variante).
- **Carrito**: `Carrito` (uno por usuario), `ItemsCarrito` (variante + cantidad).
- **Órdenes y pagos**: `Orden`, `ItemsOrden`, `Pagos`, `Entregas`, `Facturas`.
- **Soporte operativo**: `Devoluciones`, `MovimientosInventario`, `Notificaciones`.

Detalles relevantes:

- `Usuario` extiende `AbstractBaseUser` + `PermissionsMixin`, usa `email` como `USERNAME_FIELD` y está configurado como `AUTH_USER_MODEL = 'core.Usuario'`.
- `Articulos.precio_con_impuesto` y `VariantesArticulos.precio_final` calculan el precio con impuesto incluido a partir del precio base + precio extra de la variante.
- `ArticuloDescuento.precio_calculado` valida vigencia (`valido_desde`/`valido_hasta`) y cantidad restante antes de aplicar el descuento (porcentaje o valor fijo) sobre `precio_final`.
- Todas las tablas mapean a nombres `SH_*` en la base de datos (`db_table`), pensado para una base SQL Server ya existente/compartida.

## Requisitos previos

- **Ubuntu** (probado en Ubuntu sobre WSL2) con `python3`, `python3-venv`, `python3-dev`, `build-essential` y `git`.
- **Python 3.11+**.
- **SQL Server** accesible (local, en Docker o remoto) con la base de datos creada.
- **Microsoft ODBC Driver 18 for SQL Server** (`msodbcsql18`) y `unixodbc-dev`. `settings.py` usa este driver; el 17 ya no es el configurado.

## Instalación y puesta en marcha (Ubuntu)

### 1. Dependencias del sistema

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-dev build-essential unixodbc-dev curl gnupg
```

### 2. Driver ODBC 18 de SQL Server

```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install -y msodbcsql18
odbcinst -q -d    # debe listar [ODBC Driver 18 for SQL Server]
```

### 3. Entorno virtual y dependencias de Python

```bash
git clone git@github.com:Yaniel-2003/Api_dress.git
cd Api_dress

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Variables de entorno

Crea un archivo `.env` en la raíz con los valores de la sección siguiente. **`DB_USER` y `DB_PASSWORD` son obligatorios**: si faltan, Django no arranca (`KeyError`).

### 5. Migraciones, superusuario y servidor

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Por defecto el servidor queda disponible en `http://127.0.0.1:8000/`, y la API bajo `http://127.0.0.1:8000/api/`.

> **Si SQL Server corre en Windows y usas WSL2**, `127.0.0.1` apunta a Ubuntu, no a Windows. Pon en `DB_HOST` la IP del host de Windows (en WSL2 suele ser la de `ip route show | grep default`) y habilita TCP/IP en el puerto 1433.

## Variables de entorno

El archivo `.env` se carga desde `config/settings.py` con `python-dotenv`. Variables que **realmente se leen**:

| Variable | Descripción | Por defecto |
|---|---|---|
| `DB_NAME` | Nombre de la base de datos | `shopy_dress` |
| `DB_USER` | Usuario de SQL Server | **obligatoria** |
| `DB_PASSWORD` | Contraseña de SQL Server | **obligatoria** |
| `DB_HOST` | Host de SQL Server | `127.0.0.1` |
| `DB_PORT` | Puerto de SQL Server | `1433` |

Ejemplo de `.env`:

```env
DB_NAME=shopy_dress
DB_USER=sa
DB_PASSWORD=tu-password
DB_HOST=127.0.0.1
DB_PORT=1433
```

El motor (`mssql`), el driver (`ODBC Driver 18 for SQL Server`) y la opción `TrustServerCertificate=yes` están fijos en `settings.py`. Si tu `.env` trae `DEBUG`, `SECRET_KEY`, `DB_ENGINE` o `DB_DRIVER`, **hoy no se leen** (ver [Notas](#notas-y-puntos-a-mejorar)).

`CORS_ALLOWED_ORIGINS` está fijado en `settings.py` a `http://localhost:5173` y `http://127.0.0.1:5173` (el puerto por defecto de Vite). Si el front corre en otro host/puerto, hay que actualizarlo ahí. `FRONTEND_URL` (usado en el correo de recuperación) también está fijo en `http://localhost:5173`.

## Autenticación (JWT)

La API usa `rest_framework_simplejwt` como único backend de autenticación (`DEFAULT_AUTHENTICATION_CLASSES`).

- **Login**: `POST /api/login/` con `{ "email": "...", "password": "..." }` → responde `access`, `refresh` y los datos del `usuario`.
- **Uso del token**: enviar `Authorization: Bearer <access>` en cada request a un endpoint protegido.
- **Refresco**: `POST /api/token/refresh/` con el `refresh` token.
- **Logout**: `POST /api/logout/` (requiere estar autenticado) con `{ "refresh": "..." }`.
- **Recuperar contraseña**: `POST /api/password-reset/` (público, con throttling) envía un enlace por correo; `POST /api/password-reset/confirm/` fija la nueva contraseña. En desarrollo el correo se imprime en la consola del servidor (`EMAIL_BACKEND` de consola).
- **Duración**: access token 1 día, refresh token 7 días (`SIMPLE_JWT` en `settings.py`).
- El claim de usuario usa `idusuario` (UUID) en vez del `id` numérico por defecto de Django (`USER_ID_FIELD`).

> El registro de usuarios se hace por `POST /api/usuario/`, que es público.

## Endpoints de la API

Todos los endpoints cuelgan del prefijo `/api/`.

### Autenticación

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| POST | `/api/login/` | Público | Inicia sesión y devuelve tokens JWT |
| POST | `/api/token/` | Público | Par de tokens estándar de SimpleJWT |
| POST | `/api/token/refresh/` | Público | Renueva el access token |
| POST | `/api/logout/` | Autenticado | Invalida el refresh token |
| POST | `/api/password-reset/` | Público | Envía el correo de recuperación |
| POST | `/api/password-reset/confirm/` | Público | Confirma la nueva contraseña |

### Usuarios

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/usuario/` | Autenticado | Lista usuarios (filtros `?buscar=`, `?documento=`, `?nombre=`) |
| POST | `/api/usuario/` | Público | Registro de nuevo usuario |
| GET/PUT/PATCH/DELETE | `/api/usuario/{id}/` | Autenticado | Detalle / actualización / borrado |

### Direcciones

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET/POST | `/api/direcciones/` | Autenticado | Listar / crear direcciones (filtro `?buscar=`) |
| GET/PUT/PATCH/DELETE | `/api/direcciones/{id}/` | Autenticado | Detalle / actualización / borrado |

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
| GET | `/api/tienda-publica/` | **Público** | Vitrina pública: solo variantes con `stock > 0` y artículo activo, con descuentos precargados |
| GET | `/api/variantes/{idvararticulo}/fotos/` | Autenticado | Lista las fotos de una variante |
| GET/POST | `/api/descuento-articulos/` | Autenticado | Listar/crear descuentos aplicados a variantes |
| GET/PUT/PATCH/DELETE | `/api/descuento-articulos/{id}/` | Autenticado | Detalle / actualización / borrado |

### Carrito de compras

El carrito pertenece al usuario autenticado: cada consulta se filtra por `request.user`.

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| GET | `/api/carritos-compras/` | Autenticado | Lista los ítems del carrito del usuario |
| PATCH | `/api/carritos-compras/{iditmcarrito}/` | Autenticado | Actualiza un ítem (p. ej. la `cantidad`) |
| DELETE | `/api/carritos-compras/{iditmcarrito}/` | Autenticado | Quita un ítem del carrito |
| POST | `/api/agregar_item_carrito/{idvararticulo}/` | Autenticado | Agrega una variante al carrito; si ya estaba, suma 1 a la cantidad. Crea el carrito si no existe |

Todos los listados (excepto los que declaran su propia paginación) usan `PaginacionGlobal`: 50 resultados por página, máximo 100.

## Archivos de media

Las fotos de las variantes de producto (`VariantesArticulos.foto`, `FotoVarianteArticulo.archivo`) se guardan en disco bajo `MEDIA_ROOT` y se sirven en desarrollo (`DEBUG=True`) desde `MEDIA_URL = /media/`.

> **Pendiente para Ubuntu:** `MEDIA_ROOT` sigue apuntando a una ruta de Windows (`C:\Users\PC\...\Fotos_articulos`). En Linux esa ruta no existe, así que Django crearía una carpeta con ese nombre literal dentro del proyecto. Antes de subir o servir fotos, cámbialo por una ruta relativa, por ejemplo `MEDIA_ROOT = BASE_DIR / 'Fotos_articulos'`.

## Panel de administración

Disponible en `/admin/` con el tema **Jazzmin**. Ahí se gestionan directamente los catálogos (género, marca, color, talla, impuesto, descuento, cupón, categoría, prenda, permisos) y los usuarios (`UsuarioAdmin`, con búsqueda por email/nombre/apellidos/número y filtros por estado/perfil). El campo `password` es de solo lectura en el admin: se gestiona vía registro o `manage.py changepassword`.

## Notas y puntos a mejorar

Cosas detectadas al revisar el código que vale la pena tener en cuenta antes de llevar esto a producción:

- **`SECRET_KEY` y `DEBUG` hardcodeados**: `settings.py` trae un `SECRET_KEY` de ejemplo (`django-insecure-...`) y `DEBUG = True` escritos en el código; los valores del `.env` no se leen. Para producción hay que leerlos de variables de entorno y poner `ALLOWED_HOSTS`.
- **Contraseña antigua en el historial de git**: hasta el commit `c3de03e` `settings.py` traía una contraseña de base de datos como *fallback*. Ya se quitó (ahora `DB_USER`/`DB_PASSWORD` son obligatorias), pero sigue en el historial del repositorio: conviene **cambiar esa contraseña** en SQL Server.
- **`MEDIA_ROOT` con ruta absoluta de Windows**: ver [Archivos de media](#archivos-de-media).
- **Typo en JWT**: `SIMPLE_JWT` define `ROTATE_REFRECH_TOKEN`, pero la opción real de SimpleJWT es `ROTATE_REFRESH_TOKENS`; tal como está, la rotación de refresh tokens no se activa.
- **Typo en paginación**: `PaginacionGlobal.pague_size_query_param` (en `core/paginacion.py`) debería llamarse `page_size_query_param`; tal como está, DRF no lo reconoce y el tamaño de página no se puede sobreescribir por query param.
- **Subida de fotos deshabilitada**: el método `POST` de `Fotos_articulos` (subir fotos de una variante) está comentado en `core/views/articulos_views.py`; hoy el endpoint solo permite `GET`.
- **Enlace de recuperación sin pantalla en el front**: el correo apunta a `{FRONTEND_URL}/reset-password?uid=...&token=...`, pero el front todavía no tiene esa ruta.
- **Carrito sin validaciones**: `agregar_item_carrito` no comprueba el `stock` de la variante ni responde 404 limpio si el `idvararticulo` no existe.
