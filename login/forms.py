from django import forms
from .models import user, login, Grado

class userForm(forms.ModelForm):
    class Meta:
        model = user
        fields = ['Ti', 'nombre', 'apellido', 'correo', 'grado', 'password']
        widgets = {
            'Ti': forms.NumberInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'grado': forms.Select(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }