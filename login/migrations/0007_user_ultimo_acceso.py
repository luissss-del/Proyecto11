from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0006_grado_alter_login_id_alter_tokenrecuperacion_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='ultimo_acceso',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]