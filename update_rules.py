import os
import django

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

    from core.models import Prendas, Cat_Reglas_Tallaje, Tallas

    try:
        regla_sup = Cat_Reglas_Tallaje.objects.get(nombre="Parte Superior")
        regla_inf = Cat_Reglas_Tallaje.objects.get(nombre="Parte Inferior")
        regla_acc = Cat_Reglas_Tallaje.objects.get(nombre="Accesorios")

        # 1. Cambiar la regla de Ropa Interior a la misma de las Camisas (Parte Superior)
        try:
            ropa_int = Prendas.objects.get(nombre="Ropa interior")
            ropa_int.regla_tallaje = regla_sup
            ropa_int.save()
            print("Prenda 'Ropa interior' reasignada a la regla 'Parte Superior'.")
        except Prendas.DoesNotExist:
            print("No se encontro 'Ropa interior'.")

        # 2. Asignar las Tallas existentes a las Reglas
        for talla in Tallas.objects.all():
            if talla.tipo == "Camisa":
                talla.regla_tallaje = regla_sup
            elif talla.tipo == "Pantalón" or talla.tipo == "Pantalon" or talla.tipo == "Pantal\u00f3n":
                talla.regla_tallaje = regla_inf
            elif talla.tipo == "Calzado":
                talla.regla_tallaje = regla_acc
            
            if talla.regla_tallaje:
                talla.save()
                print(f"Talla {talla.codigo} ({talla.tipo}) -> {talla.regla_tallaje.nombre}")

    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
