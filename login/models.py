from django.db import models
import uuid
from django.utils import timezone

# Create your models here.
class user(models.Model):
    Ti = models.IntegerField()
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    es_admin = models.BooleanField(default=False)
    grado = models.ForeignKey('Grado', on_delete=models.SET_NULL, null=True, blank=True, related_name='estudiantes')
    def __str__(self):
        return f"{self.nombre} {self.apellido} {self.password}"

class login(models.Model):
    nombre   = models.ForeignKey(user, on_delete=models.CASCADE, related_name='login_nombre')
    password = models.ForeignKey(user, on_delete=models.CASCADE, related_name='login_password')
    
    def __str__(self):
        return f"{self.nombre} {self.password}"

class TokenRecuperacion(models.Model):
    usuario   = models.ForeignKey('user', on_delete=models.CASCADE, related_name='tokens')
    token     = models.UUIDField(default=uuid.uuid4, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    usado     = models.BooleanField(default=False)

    def esta_vigente(self):
        return not self.usado and (timezone.now() - self.creado_en).seconds < 3600

    def __str__(self):
        return f"Token de {self.usuario.nombre}"

class Grado(models.Model):
    nombre = models.CharField(max_length=10, unique=True)
    orden  = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.nombre
