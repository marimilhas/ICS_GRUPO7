# entradas/migrations/0002_seed_initial_passes.py

from django.db import migrations


def create_initial_passes(apps, schema_editor):
    """Inserta los dos tipos de pase esenciales (Regular y VIP) con sus precios."""
    # Obtenemos el modelo 'Pase' tal como lo conoce esta migración
    Pase = apps.get_model('entradas', 'Pase')

    # Los datos iniciales definidos por tu lógica de negocio
    initial_data = [
        {"tipo": "Regular", "precio": 5000.00},
        {"tipo": "VIP", "precio": 10000.00},
    ]

    for data in initial_data:
        # Crea o actualiza el registro. Esto evita errores si la migración se corre varias veces.
        Pase.objects.update_or_create(
            tipo=data["tipo"],
            defaults={'precio': data["precio"]}
        )


# Función inversa para cuando se revierte la migración
def remove_initial_passes(apps, schema_editor):
    """Borra los pases creados en esta migración."""
    Pase = apps.get_model('entradas', 'Pase')
    Pase.objects.filter(tipo__in=["Regular", "VIP"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        # Asegúrate de que apunte a la migración que crea la tabla 'Pase'
        ('entradas', '0001_initial'),
    ]

    operations = [
        # Ejecuta la función de inserción y define la función de reversión
        migrations.RunPython(create_initial_passes, remove_initial_passes),
    ]