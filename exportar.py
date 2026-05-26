import os
import django
from django.conf import settings

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
        'login',
        'paises',
    ],
    DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
)

django.setup()

from django.core.management import call_command
with open('datos.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', '--natural-foreign', '--natural-primary',
                 '--exclude=contenttypes', '--exclude=auth.permission', stdout=f)

print("Listo!")