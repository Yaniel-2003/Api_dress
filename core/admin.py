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
admin.site.register(Prendas)
admin.site.register(Permission)
admin.site.register(Cat_Reglas_Tallaje)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('email', 'nombres', 'apellidos', 'perfil',
                    'is_active', 'is_staff', 'is_superuser', 'fecha_creacion')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'perfil')
    search_fields = ('email', 'nombres', 'apellidos', 'numero')
    ordering = ('-fecha_creacion',)
    # password se maneja fuera del admin: registro / createsuperuser / changepassword
    readonly_fields = ('password', 'last_login', 'fecha_creacion')