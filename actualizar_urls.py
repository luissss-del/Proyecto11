import os
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.path.dirname(__file__), 'db.sqlite3'),
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'epocas',
        ],
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
    )

django.setup()

from epocas.models import Material, MaterialPais, MaterialEpoca

base_cloudinary = "https://res.cloudinary.com/dkcrrnukk/raw/upload/"

modelos = [Material, MaterialPais, MaterialEpoca]

for modelo in modelos:
    for obj in modelo.objects.all():
        if obj.archivo and not str(obj.archivo).startswith("http"):
            ruta = str(obj.archivo).replace("materiales/", "")
            obj.archivo = base_cloudinary + ruta
            obj.save()
            print(f"✓ {obj.archivo}")

print("Listo!")