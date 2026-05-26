from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epocas', '0008_material_grados_material_todos_los_grados_and_more'),
    ]

    operations = [
        # Ampliar slug para que acepte slugs libres (no solo ww1/ww2/cf)
        migrations.AlterField(
            model_name='epoca',
            name='slug',
            field=models.CharField(max_length=50, unique=True),
        ),
        # Agregar campo icono (emoji de la tarjeta)
        migrations.AddField(
            model_name='epoca',
            name='icono',
            field=models.CharField(default='📖', max_length=10),
        ),
        # Agregar campo orden para controlar el orden de aparición en el home
        migrations.AddField(
            model_name='epoca',
            name='orden',
            field=models.IntegerField(default=0),
        ),
    ]