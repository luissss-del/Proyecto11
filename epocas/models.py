from django.db import models
from django.utils.text import slugify


class Epoca(models.Model):
    # slug: identificador único en la URL, ej. "ww1", "revolucion-francesa"
    # Se genera automáticamente desde el nombre si no se pone uno manual.
    slug        = models.CharField(max_length=50, unique=True)
    nombre      = models.CharField(max_length=100)
    # Años de inicio y fin que aparecen en la tarjeta, ej. 1914 / 1918
    anio_inicio = models.IntegerField()
    anio_fin    = models.IntegerField()
    # Texto corto que aparece debajo del título en la tarjeta del home
    descripcion = models.TextField()
    # Emoji o símbolo que aparece grande en la tarjeta, ej. ⚔️ 🌍 ☢️
    icono       = models.CharField(max_length=10, default='📖')
    # Color principal de la tarjeta en formato hex, ej. #c9a84c
    color_hex   = models.CharField(max_length=7, default='#c9a84c')
    # Orden de aparición en el home (1 = primera tarjeta)
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden', 'anio_inicio']

    def save(self, *args, **kwargs):
        # Si no tiene slug, lo genera desde el nombre automáticamente
        if not self.slug:
            base = slugify(self.nombre)
            slug = base
            n = 1
            while Epoca.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

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


    def get_url(self):
        if self.archivo:
            url = self.archivo.url
            if 'cloudinary' in url:
                url = url.replace('/image/upload/', '/raw/upload/')
                url = url.replace('/video/upload/', '/raw/upload/')
                return url
            return url
        return self.url or ''


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


    def get_url(self):
        if self.archivo:
            url = self.archivo.url
            if 'cloudinary' in url:
                url = url.replace('/image/upload/', '/raw/upload/')
                url = url.replace('/video/upload/', '/raw/upload/')
                return url
            return url
        return self.url or ''


class PuntoMapa(models.Model):
    TIPO_CHOICES = [
        ('batalla',   'Batalla'),
        ('ciudad',    'Ciudad clave'),
        ('frente',    'Frente de guerra'),
        ('ruta',      'Ruta de avance'),
        ('zona',      'Zona estratégica'),
        ('otro',      'Otro'),
    ]
    BANDO_CHOICES = [
        ('aliados',  'Aliados'),
        ('enemigos', 'Potencias Enemigas'),
        ('neutral',  'Neutral'),
        ('otro',     'Otro'),
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
    coordenadas = models.JSONField()
    orden       = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"Zona: {self.nombre} — {self.evento.titulo}"


class LineaMapa(models.Model):
    TIPO_CHOICES = [
        ('frente',   'Frente de guerra'),
        ('ruta',     'Ruta de avance'),
        ('retirada', 'Ruta de retirada'),
        ('naval',    'Ruta naval'),
        ('otro',     'Otro'),
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
    coordenadas = models.JSONField()
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


    def get_url(self):
        if self.archivo:
            url = self.archivo.url
            if 'cloudinary' in url:
                url = url.replace('/image/upload/', '/raw/upload/')
                url = url.replace('/video/upload/', '/raw/upload/')
                return url
            return url
        return self.url or ''