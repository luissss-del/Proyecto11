from django.contrib import admin
from .models import Epoca, Pais, Evento, Material


@admin.register(Epoca)
class EpocaAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'slug', 'anio_inicio', 'anio_fin']
    ordering      = ['anio_inicio']


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'epoca', 'tipo', 'bando', 'orden']
    list_filter   = ['epoca', 'tipo']
    ordering      = ['epoca', 'orden']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display  = ['titulo', 'anio', 'epoca', 'orden']
    list_filter   = ['epoca']
    ordering      = ['epoca', 'orden', 'anio']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display  = ['titulo', 'tipo', 'evento', 'subido_en']
    list_filter   = ['tipo', 'evento__epoca']