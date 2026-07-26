from django.contrib import admin
from django.contrib.auth.models import Permission

from .models import *

admin.site.register(Genero)
admin.site.register(NunDocumento)
admin.site.register(Perfil)
admin.site.register(Marcas)
admin.site.register(Colores)
admin.site.register(Tallas)
admin.site.register(Impuestos)
admin.site.register(Descuentos)
admin.site.register(Cupones)
admin.site.register(Categoria)
admin.site.register(TiposPrendas)
admin.site.register(Permission)