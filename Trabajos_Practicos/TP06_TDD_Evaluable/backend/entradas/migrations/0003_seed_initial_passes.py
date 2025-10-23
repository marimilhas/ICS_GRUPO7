from django.db import migrations

def create_initial_passes(apps, schema_editor):
    Pase = apps.get_model('entradas', 'Pase')
    initial_data = [
        {"tipo": "Regular", "precio": 5000.00},
        {"tipo": "VIP", "precio": 10000.00},
    ]
    for data in initial_data:
        Pase.objects.update_or_create(
            tipo=data["tipo"],
            defaults={'precio': data["precio"]}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('entradas', '0002_remove_pase_nombre_pase_tipo'),
    ]

    operations = [
        migrations.RunPython(create_initial_passes),
    ]
