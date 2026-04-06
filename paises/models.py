from django.db import models


class Continente(models.Model):
    nombre    = models.CharField(max_length=100)
    slug      = models.CharField(max_length=20, unique=True)
    icono     = models.CharField(max_length=10, default='🌍')
    orden     = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return self.nombre


class Region(models.Model):
    continente = models.ForeignKey(Continente, on_delete=models.CASCADE, related_name='regiones')
    nombre     = models.CharField(max_length=100)
    slug       = models.CharField(max_length=30, unique=True)
    orden      = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nombre} ({self.continente.nombre})"


class Pais(models.Model):
    region           = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='paises')
    nombre           = models.CharField(max_length=100)
    slug             = models.CharField(max_length=50, unique=True)
    bandera          = models.CharField(max_length=10, blank=True)   # emoji
    codigo_iso       = models.CharField(max_length=3, blank=True)    # ej: COL, USA
    capital          = models.CharField(max_length=100, blank=True)
    idioma_oficial   = models.CharField(max_length=100, blank=True)
    poblacion        = models.CharField(max_length=50, blank=True)   # ej: "52 millones"
    superficie       = models.CharField(max_length=50, blank=True)   # ej: "1.141.748 km²"
    descripcion      = models.TextField(blank=True)
    historia         = models.TextField(blank=True)
    conflictos       = models.TextField(blank=True)
    color_bandera1   = models.CharField(max_length=7, default='#f5f5f5')  # color principal
    color_bandera2   = models.CharField(max_length=7, default='#cccccc')  # color secundario
    lat_centro       = models.FloatField(default=0.0)   # coordenada centro del país
    lng_centro       = models.FloatField(default=0.0)
    zoom_inicial     = models.IntegerField(default=5)   # zoom del mapa
    orden            = models.IntegerField(default=0)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class CiudadPais(models.Model):
    TIPO_CHOICES = [
        ('capital',      'Capital'),
        ('principal',    'Ciudad principal'),
        ('historica',    'Ciudad histórica'),
        ('conflicto',    'Zona de conflicto'),
    ]
    pais        = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='ciudades')
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES, default='principal')
    latitud     = models.FloatField()
    longitud    = models.FloatField()
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nombre} — {self.pais.nombre}"


class MaterialPaisSeccion(models.Model):
    TIPO_CHOICES = [
        ('pdf',   'PDF'),
        ('video', 'Video'),
        ('link',  'Enlace web'),
        ('word',  'Word'),
    ]
    pais      = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='materiales')
    tipo      = models.CharField(max_length=10, choices=TIPO_CHOICES)
    titulo    = models.CharField(max_length=200)
    url       = models.URLField(blank=True)
    archivo   = models.FileField(upload_to='materiales/paises_seccion/', blank=True, null=True)
    subido_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} — {self.pais.nombre}"