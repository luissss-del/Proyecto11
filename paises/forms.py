from django import forms
from .models import Pais, CiudadPais, MaterialPaisSeccion


class PaisForm(forms.ModelForm):
    class Meta:
        model  = Pais
        fields = ['descripcion', 'historia', 'conflictos', 'capital',
                  'idioma_oficial', 'poblacion', 'superficie',
                  'color_bandera1', 'color_bandera2']
        widgets = {
            'descripcion':    forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 4}),
            'historia':       forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 6}),
            'conflictos':     forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 6}),
            'capital':        forms.TextInput(attrs={'class': 'edit-input'}),
            'idioma_oficial': forms.TextInput(attrs={'class': 'edit-input'}),
            'poblacion':      forms.TextInput(attrs={'class': 'edit-input'}),
            'superficie':     forms.TextInput(attrs={'class': 'edit-input'}),
            'color_bandera1': forms.TextInput(attrs={'class': 'edit-input edit-input--sm', 'type': 'color'}),
            'color_bandera2': forms.TextInput(attrs={'class': 'edit-input edit-input--sm', 'type': 'color'}),
        }


class CiudadPaisForm(forms.ModelForm):
    class Meta:
        model  = CiudadPais
        fields = ['nombre', 'tipo', 'descripcion', 'latitud', 'longitud', 'orden']
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'edit-input'}),
            'tipo':        forms.Select(attrs={'class': 'edit-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'edit-textarea', 'rows': 3}),
            'latitud':     forms.NumberInput(attrs={'class': 'edit-input edit-input--sm', 'step': 'any'}),
            'longitud':    forms.NumberInput(attrs={'class': 'edit-input edit-input--sm', 'step': 'any'}),
            'orden':       forms.NumberInput(attrs={'class': 'edit-input edit-input--sm'}),
        }


class MaterialPaisSeccionForm(forms.ModelForm):
    class Meta:
        model  = MaterialPaisSeccion
        fields = ['tipo', 'titulo', 'url', 'archivo']
        widgets = {
            'tipo':    forms.Select(attrs={'class': 'edit-select'}),
            'titulo':  forms.TextInput(attrs={'class': 'edit-input'}),
            'url':     forms.URLInput(attrs={'class': 'edit-input', 'placeholder': 'https://...'}),
            'archivo': forms.FileInput(attrs={'class': 'edit-file'}),
        }