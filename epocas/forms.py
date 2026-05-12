from django import forms
from .models import Evento, Pais, Material, MaterialPais, MaterialEpoca, Epoca


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARIO DE ÉPOCA
# ══════════════════════════════════════════════════════════════════════════════
class EpocaForm(forms.ModelForm):
    class Meta:
        model  = Epoca
        # Campos que la profesora completa al crear/editar una época
        fields = ['nombre', 'anio_inicio', 'anio_fin', 'descripcion', 'icono', 'color_hex', 'orden']
        widgets = {
            # Nombre completo de la época, ej: "Revolución Francesa"
            'nombre':      forms.TextInput(attrs={
                'class': 'edit-input',
                'placeholder': 'ej. Revolución Francesa',
            }),
            # Año en que comenzó el período histórico, ej: 1789
            'anio_inicio': forms.NumberInput(attrs={
                'class': 'edit-input edit-input--sm',
                'placeholder': 'ej. 1789',
            }),
            # Año en que terminó el período histórico, ej: 1799
            'anio_fin':    forms.NumberInput(attrs={
                'class': 'edit-input edit-input--sm',
                'placeholder': 'ej. 1799',
            }),
            # Texto corto que aparece en la tarjeta del home describiendo la época
            'descripcion': forms.Textarea(attrs={
                'class': 'edit-textarea',
                'rows': 3,
                'placeholder': 'Breve descripción que verán los estudiantes en la tarjeta del inicio.',
            }),
            # Emoji que aparece grande en el centro de la tarjeta
            # Busca emojis en: https://emojipedia.org
            # Ejemplos: ⚔️ para guerra, 🌍 para mundial, ☢️ para nuclear, 🏛️ para antigüedad
            'icono':       forms.TextInput(attrs={
                'class': 'edit-input edit-input--sm',
                'placeholder': 'ej. ⚔️',
            }),
            # Color principal de la tarjeta en formato hexadecimal
            # Usa el selector de color haciendo clic en el cuadro de color
            # Ejemplos: #c9a84c (dorado), #e74c3c (rojo), #3498db (azul), #2ecc71 (verde)
            'color_hex':   forms.TextInput(attrs={
                'class': 'edit-input edit-input--sm',
                'type':  'color',
            }),
            # Número de orden de aparición en el home (1 = primera tarjeta, 2 = segunda, etc.)
            'orden':       forms.NumberInput(attrs={
                'class': 'edit-input edit-input--sm',
                'placeholder': 'ej. 4',
            }),
        }


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARIO DE EVENTO
# ══════════════════════════════════════════════════════════════════════════════
class EventoForm(forms.ModelForm):
    class Meta:
        model  = Evento
        fields = ['titulo', 'anio', 'mes', 'icono', 'resumen', 'descripcion', 'orden']
        widgets = {
            # Título del evento histórico
            'titulo':      forms.TextInput(attrs={'class': 'edit-input'}),
            # Año en que ocurrió el evento
            'anio':        forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
            # Mes (opcional): 1=enero ... 12=diciembre. Dejar vacío si no se conoce el mes exacto
            'mes':         forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
            # Emoji representativo del evento, ej. 💣 🗡️ 🚢
            'icono':       forms.TextInput(attrs={'class': 'edit-input edit-input--sm'}),
            # Resumen corto (máx. 300 caracteres) que aparece en la lista de eventos
            'resumen':     forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 2}),
            # Descripción completa y detallada del evento para los estudiantes
            'descripcion': forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 6}),
            # Orden de aparición dentro de la época (1 = primer evento)
            'orden':       forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
        }


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARIO DE PAÍS
# ══════════════════════════════════════════════════════════════════════════════
class PaisForm(forms.ModelForm):
    class Meta:
        model  = Pais
        fields = ['nombre', 'bandera', 'tipo', 'bando', 'descripcion', 'orden']
        widgets = {
            # Nombre del país, ej. "Alemania", "Francia", "Reino Unido"
            'nombre':      forms.TextInput(attrs={'class': 'edit-input'}),
            # Emoji de la bandera del país, ej. 🇩🇪 🇫🇷 🇬🇧
            # Busca banderas en: https://emojipedia.org/flags
            'bandera':     forms.TextInput(attrs={'class': 'edit-input edit-input--sm'}),
            # Tipo: "Principal" = país central en el conflicto / "Colateral" = participó secundariamente
            'tipo':        forms.Select(attrs={'class': 'edit-select'}),
            # Bando al que pertenecía, ej. "Aliados", "Potencias Centrales", "Eje"
            'bando':       forms.TextInput(attrs={'class': 'edit-input'}),
            # Descripción del rol del país en la época
            'descripcion': forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 5}),
            # Orden de aparición en la lista de países (1 = primero)
            'orden':       forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
        }


class MaterialForm(forms.ModelForm):
    class Meta:
        model  = Material
        fields = ['tipo', 'titulo', 'url', 'archivo', 'todos_los_grados', 'grados']
        widgets = {
            # Tipo de material: PDF, Video, Enlace web, Word
            'tipo':             forms.Select(attrs={'class': 'edit-select'}),
            # Nombre del material que verán los estudiantes
            'titulo':           forms.TextInput(attrs={'class': 'edit-input'}),
            # URL del video o enlace (si el tipo es Video o Enlace web)
            'url':              forms.URLInput(attrs={'class': 'edit-input', 'placeholder': 'https://...'}),
            # Archivo a subir (si el tipo es PDF o Word)
            'archivo':          forms.FileInput(attrs={'class': 'edit-file'}),
            # Marcar si el material es para TODOS los grados
            'todos_los_grados': forms.CheckboxInput(attrs={'class': 'grados-toggle-check'}),
            # Si no es para todos, selecciona los grados específicos
            'grados':           forms.CheckboxSelectMultiple(attrs={'class': 'grados-check-list'}),
        }


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARIO DE MATERIAL DE PAÍS
# ══════════════════════════════════════════════════════════════════════════════
class MaterialPaisForm(forms.ModelForm):
    class Meta:
        model  = MaterialPais
        fields = ['tipo', 'titulo', 'url', 'archivo', 'todos_los_grados', 'grados']
        widgets = {
            'tipo':             forms.Select(attrs={'class': 'edit-select'}),
            'titulo':           forms.TextInput(attrs={'class': 'edit-input'}),
            'url':              forms.URLInput(attrs={'class': 'edit-input', 'placeholder': 'https://...'}),
            'archivo':          forms.FileInput(attrs={'class': 'edit-file'}),
            'todos_los_grados': forms.CheckboxInput(attrs={'class': 'grados-toggle-check'}),
            'grados':           forms.CheckboxSelectMultiple(attrs={'class': 'grados-check-list'}),
        }


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARIO DE MATERIAL DE ÉPOCA
# ══════════════════════════════════════════════════════════════════════════════
class MaterialEpocaForm(forms.ModelForm):
    class Meta:
        model  = MaterialEpoca
        fields = ['tipo', 'titulo', 'url', 'archivo', 'todos_los_grados', 'grados']
        widgets = {
            'tipo':             forms.Select(attrs={'class': 'edit-select'}),
            'titulo':           forms.TextInput(attrs={'class': 'edit-input'}),
            'url':              forms.URLInput(attrs={'class': 'edit-input', 'placeholder': 'https://...'}),
            'archivo':          forms.FileInput(attrs={'class': 'edit-file'}),
            'todos_los_grados': forms.CheckboxInput(attrs={'class': 'grados-toggle-check'}),
            'grados':           forms.CheckboxSelectMultiple(attrs={'class': 'grados-check-list'}),
        }