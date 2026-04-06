from django import forms
from .models import Evento, Pais, Material, MaterialPais, MaterialEpoca


class EventoForm(forms.ModelForm):
    class Meta:
        model  = Evento
        fields = ['titulo', 'anio', 'mes', 'icono', 'resumen', 'descripcion', 'orden']
        widgets = {
            'titulo':      forms.TextInput(attrs={'class': 'edit-input'}),
            'anio':        forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
            'mes':         forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
            'icono':       forms.TextInput(attrs={'class': 'edit-input edit-input--sm'}),
            'resumen':     forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 2}),
            'descripcion': forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 6}),
            'orden':       forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
        }


class PaisForm(forms.ModelForm):
    class Meta:
        model  = Pais
        fields = ['nombre', 'bandera', 'tipo', 'bando', 'descripcion', 'orden']
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'edit-input'}),
            'bandera':     forms.TextInput(attrs={'class': 'edit-input edit-input--sm'}),
            'tipo':        forms.Select(attrs={'class': 'edit-select'}),
            'bando':       forms.TextInput(attrs={'class': 'edit-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 5}),
            'orden':       forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
        }


class MaterialForm(forms.ModelForm):
    class Meta:
        model  = Material
        fields = ['tipo', 'titulo', 'url', 'archivo', 'todos_los_grados', 'grados']
        widgets = {
            'tipo':             forms.Select(attrs={'class': 'edit-select'}),
            'titulo':           forms.TextInput(attrs={'class': 'edit-input'}),
            'url':              forms.URLInput(attrs={'class': 'edit-input', 'placeholder': 'https://...'}),
            'archivo':          forms.FileInput(attrs={'class': 'edit-file'}),
            'todos_los_grados': forms.CheckboxInput(attrs={'class': 'grados-toggle-check'}),
            'grados':           forms.CheckboxSelectMultiple(attrs={'class': 'grados-check-list'}),
        }


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
