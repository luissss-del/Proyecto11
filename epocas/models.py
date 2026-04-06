from django.db import models


class Epoca(models.Model):
    EPOCAS_CHOICES = [
        ('ww1', 'Primera Guerra Mundial'),
        ('ww2', 'Segunda Guerra Mundial'),
        ('cf',  'Guerra Fría'),
    ]
    slug        = models.CharField(max_length=10, unique=True, choices=EPOCAS_CHOICES)
    nombre      = models.CharField(max_length=100)
    anio_inicio = models.IntegerField()
    anio_fin    = models.IntegerField()
    descripcion = models.TextField()
    color_hex   = models.CharField(max_length=7, default='#c9a84c')

    def __str__(self):
        return self.nombre


class Pais(models.Model):
    TIPO_CHOICES = [
        ('principal', 'Principal'),
        ('colateral', 'Colateral'),
    ]
    epoca       = models.ForeignKey(Epoca, on_delete=models.CASCADE, related_name='paises')
    nombre      = models.CharField(max_length=100)
    bandera     = models.CharField(max_length=10, blank=True)
    tipo        = models.CharField(max_length=10, choices=TIPO_CHOICES, default='principal')
    bando       = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField()
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.epoca.slug})"


class Evento(models.Model):
    epoca       = models.ForeignKey(Epoca, on_delete=models.CASCADE, related_name='eventos')
    titulo      = models.CharField(max_length=200)
    anio        = models.IntegerField()
    mes         = models.IntegerField(blank=True, null=True)
    resumen     = models.CharField(max_length=300)
    descripcion = models.TextField()
    icono       = models.CharField(max_length=10, blank=True)
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden', 'anio', 'mes']

    def __str__(self):
        return f"[{self.anio}] {self.titulo}"


class Material(models.Model):
    """Material de apoyo para un evento."""
    TIPO_CHOICES = [
        ('pdf',   'PDF'),
        ('video', 'Video (link)'),
        ('link',  'Enlace web'),
        ('word',  'Word'),
    ]
    evento            = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='materiales')
    tipo              = models.CharField(max_length=10, choices=TIPO_CHOICES)
    titulo            = models.CharField(max_length=200)
    url               = models.URLField(blank=True)
    archivo           = models.FileField(upload_to='materiales/eventos/', blank=True, null=True)
    subido_en         = models.DateTimeField(auto_now_add=True)
    todos_los_grados  = models.BooleanField(default=True)
    grados            = models.ManyToManyField('login.Grado', blank=True, related_name='materiales_evento')

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"


class MaterialPais(models.Model):
    """Material de apoyo para un país dentro de una época."""
    TIPO_CHOICES = [
        ('pdf',   'PDF'),
        ('video', 'Video (link)'),
        ('link',  'Enlace web'),
        ('word',  'Word'),
    ]
    pais              = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='materiales')
    tipo              = models.CharField(max_length=10, choices=TIPO_CHOICES)
    titulo            = models.CharField(max_length=200)
    url               = models.URLField(blank=True)
    archivo           = models.FileField(upload_to='materiales/paises/', blank=True, null=True)
    subido_en         = models.DateTimeField(auto_now_add=True)
    todos_los_grados  = models.BooleanField(default=True)
    grados            = models.ManyToManyField('login.Grado', blank=True, related_name='materiales_pais')

    def __str__(self):
        return f"{self.titulo} ({self.tipo}) — {self.pais.nombre}"
    

class PuntoMapa(models.Model):
    """
    Punto geográfico asociado a un evento histórico.
    Aparece como marcador en el mapa interactivo.
    """
    TIPO_CHOICES = [
        ('batalla',   'Batalla'),
        ('ciudad',    'Ciudad clave'),
        ('frente',    'Frente de guerra'),
        ('ruta',      'Ruta de avance'),
        ('zona',      'Zona estratégica'),
        ('otro',      'Otro'),
    ]
    BANDO_CHOICES = [
        ('aliados',      'Aliados'),
        ('enemigos',     'Potencias Enemigas'),
        ('neutral',      'Neutral'),
        ('otro',         'Otro'),
    ]

    evento      = models.ForeignKey('Evento', on_delete=models.CASCADE, related_name='puntos_mapa')
    nombre      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES, default='batalla')
    bando       = models.CharField(max_length=20, choices=BANDO_CHOICES, default='neutral')
    latitud     = models.FloatField()
    longitud    = models.FloatField()
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.nombre} — {self.evento.titulo}"
    
class ZonaMapa(models.Model):
    """
    Polígono resaltado en el mapa — territorios ocupados, zonas de batalla, áreas estratégicas.
    coordenadas: JSON con lista de pares [[lat,lng], [lat,lng], ...]
    """
    BANDO_CHOICES = [
        ('aliados',  'Aliados'),
        ('enemigos', 'Potencias Enemigas'),
        ('neutral',  'Neutral'),
        ('otro',     'Otro'),
    ]
    evento      = models.ForeignKey('Evento', on_delete=models.CASCADE, related_name='zonas_mapa')
    nombre      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    bando       = models.CharField(max_length=20, choices=BANDO_CHOICES, default='neutral')
    coordenadas = models.JSONField()   # [[lat,lng], [lat,lng], ...]
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"Zona: {self.nombre} — {self.evento.titulo}"


class LineaMapa(models.Model):
    """
    Línea sobre el mapa — frentes de guerra, rutas de avance, movimientos de tropas.
    coordenadas: JSON con lista de pares [[lat,lng], [lat,lng], ...]
    """
    TIPO_CHOICES = [
        ('frente', 'Frente de guerra'),
        ('ruta',   'Ruta de avance'),
        ('retirada','Ruta de retirada'),
        ('naval',  'Ruta naval'),
        ('otro',   'Otro'),
    ]
    BANDO_CHOICES = [
        ('aliados',  'Aliados'),
        ('enemigos', 'Potencias Enemigas'),
        ('neutral',  'Neutral'),
        ('otro',     'Otro'),
    ]
    evento      = models.ForeignKey('Evento', on_delete=models.CASCADE, related_name='lineas_mapa')
    nombre      = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo        = models.CharField(max_length=20, choices=TIPO_CHOICES, default='frente')
    bando       = models.CharField(max_length=20, choices=BANDO_CHOICES, default='neutral')
    coordenadas = models.JSONField()   # [[lat,lng], [lat,lng], ...]
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"Línea: {self.nombre} — {self.evento.titulo}"

class MaterialEpoca(models.Model):
    TIPO_CHOICES = [
        ('video', 'Video'),
        ('pdf',   'PDF'),
        ('link',  'Enlace web'),
        ('word',  'Word'),
    ]
    epoca            = models.ForeignKey('Epoca', on_delete=models.CASCADE, related_name='materiales_epoca')
    tipo             = models.CharField(max_length=10, choices=TIPO_CHOICES, default='video')
    titulo           = models.CharField(max_length=200)
    url              = models.URLField(blank=True)
    archivo          = models.FileField(upload_to='materiales/epocas/', blank=True, null=True)
    subido_en        = models.DateTimeField(auto_now_add=True)
    todos_los_grados = models.BooleanField(default=True)
    grados           = models.ManyToManyField('login.Grado', blank=True, related_name='materiales_epoca')

    class Meta:
        ordering = ['subido_en']

    def __str__(self):
        return f"{self.titulo} ({self.tipo}) — {self.epoca.nombre}"