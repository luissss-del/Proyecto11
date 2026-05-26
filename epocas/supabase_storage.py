from django.conf import settings
from supabase import create_client
import uuid
import os

def get_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def subir_archivo(archivo, carpeta='eventos'):
    cliente = get_client()
    ext      = os.path.splitext(archivo.name)[1]
    nombre   = f"{carpeta}/{uuid.uuid4().hex}{ext}"
    contenido = archivo.read()
    cliente.storage.from_(settings.SUPABASE_BUCKET).upload(
        nombre,
        contenido,
        {"content-type": archivo.content_type or 'application/octet-stream'}
    )
    url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{nombre}"
    return url

def eliminar_archivo(url):
    try:
        cliente = get_client()
        path = url.split(f'/object/public/{settings.SUPABASE_BUCKET}/')[-1]
        cliente.storage.from_(settings.SUPABASE_BUCKET).remove([path])
    except:
        pass