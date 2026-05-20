from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Epoca, Evento, Pais, Material, MaterialPais, MaterialEpoca
from .forms import EpocaForm, EventoForm, PaisForm, MaterialForm, MaterialPaisForm, MaterialEpocaForm


def _check_sesion(request):
    return bool(request.session.get('usuario_id'))

def _check_admin(request):
    return request.session.get('es_admin') == True

def _ctx(request):
    return {
        'nombre':   request.session.get('usuario_nombre', 'Estudiante'),
        'es_admin': request.session.get('es_admin', False),
    }

def _get_grado_usuario(request):
    from login.models import user as User
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return None
    try:
        u = User.objects.select_related('grado').get(pk=usuario_id)
        return u.grado
    except User.DoesNotExist:
        return None

def _filtrar_materiales(queryset, grado_usuario, es_admin):
    if es_admin:
        return queryset
    if grado_usuario:
        from django.db.models import Q
        return queryset.filter(
            Q(todos_los_grados=True) | Q(grados=grado_usuario)
        ).distinct()
    return queryset.filter(todos_los_grados=True)


# ── Vistas públicas ───────────────────────────────────────────────────────────

def detalle_epoca(request, slug):
    if not _check_sesion(request):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    es_admin      = _check_admin(request)
    grado_usuario = _get_grado_usuario(request)
    epoca         = get_object_or_404(Epoca, slug=slug)
    eventos       = list(epoca.eventos.all())
    principales   = list(epoca.paises.filter(tipo='principal'))
    colaterales   = list(epoca.paises.filter(tipo='colateral'))
    materiales_epoca = _filtrar_materiales(
        epoca.materiales_epoca.prefetch_related('grados').all(),
        grado_usuario, es_admin
    )

    return render(request, 'detalle_epoca.html', {
        'epoca':               epoca,
        'eventos':             eventos,
        'principales':         principales,
        'colaterales':         colaterales,
        'materiales_epoca':    materiales_epoca,
        'form_nuevo_pais':     PaisForm(),
        'form_material_epoca': MaterialEpocaForm(),
        'grado_usuario':       grado_usuario,
        **_ctx(request),
    })


def detalle_evento(request, slug, evento_id):
    if not _check_sesion(request):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    es_admin      = _check_admin(request)
    grado_usuario = _get_grado_usuario(request)
    epoca         = get_object_or_404(Epoca, slug=slug)
    evento        = get_object_or_404(Evento, pk=evento_id, epoca=epoca)

    todos   = list(epoca.eventos.all())
    idx     = next((i for i, e in enumerate(todos) if e.pk == evento.pk), None)
    prev_ev = todos[idx - 1] if idx and idx > 0                        else None
    next_ev = todos[idx + 1] if idx is not None and idx < len(todos)-1 else None

    materiales = _filtrar_materiales(
        evento.materiales.prefetch_related('grados').all(),
        grado_usuario, es_admin
    )

    return render(request, 'detalle_evento.html', {
        'epoca':            epoca,
        'evento':           evento,
        'materiales':       materiales,
        'evento_anterior':  prev_ev,
        'evento_siguiente': next_ev,
        'form_evento':      EventoForm(instance=evento),
        'form_material':    MaterialForm(),
        'grado_usuario':    grado_usuario,
        **_ctx(request),
    })


def detalle_pais(request, slug, pais_id):
    if not _check_sesion(request):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    es_admin      = _check_admin(request)
    grado_usuario = _get_grado_usuario(request)
    epoca         = get_object_or_404(Epoca, slug=slug)
    pais          = get_object_or_404(Pais, pk=pais_id, epoca=epoca)

    materiales = _filtrar_materiales(
        pais.materiales.prefetch_related('grados').all(),
        grado_usuario, es_admin
    )

    return render(request, 'detalle_pais.html', {
        'epoca':              epoca,
        'pais':               pais,
        'materiales':         materiales,
        'form_pais':          PaisForm(instance=pais),
        'form_material_pais': MaterialPaisForm(),
        'grado_usuario':      grado_usuario,
        **_ctx(request),
    })


# ── CRUD de Épocas (solo admin) ───────────────────────────────────────────────

def crear_epoca(request):
    """
    Muestra el formulario para crear una nueva época/tarjeta en el home.
    La profesora completa: nombre, años, descripción, ícono y color.
    """
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')

    if request.method == 'POST':
        form = EpocaForm(request.POST)
        if form.is_valid():
            epoca = form.save()
            messages.success(request, f'¡Época "{epoca.nombre}" creada! Ya aparece en el inicio.')
            return redirect('detalle_epoca', slug=epoca.slug)
        else:
            messages.error(request, 'Hay errores en el formulario. Revisa los campos.')
    else:
        form = EpocaForm()

    return render(request, 'crear_epoca.html', {
        'form':   form,
        'titulo': 'Nueva época',
        **_ctx(request),
    })


def editar_epoca(request, slug):
    """
    Permite editar los datos de una época ya creada:
    nombre, años, descripción, ícono, color y orden.
    """
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')

    epoca = get_object_or_404(Epoca, slug=slug)

    if request.method == 'POST':
        form = EpocaForm(request.POST, instance=epoca)
        if form.is_valid():
            form.save()
            messages.success(request, f'Época "{epoca.nombre}" actualizada.')
            return redirect('detalle_epoca', slug=epoca.slug)
        else:
            messages.error(request, 'Hay errores en el formulario.')
    else:
        form = EpocaForm(instance=epoca)

    return render(request, 'crear_epoca.html', {
        'form':   form,
        'epoca':  epoca,
        'titulo': f'Editar — {epoca.nombre}',
        **_ctx(request),
    })


@require_POST
def eliminar_epoca(request, slug):
    """
    Elimina una época y TODO su contenido (eventos, países, materiales).
    ¡Esta acción no se puede deshacer!
    """
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')

    epoca  = get_object_or_404(Epoca, slug=slug)
    nombre = epoca.nombre
    epoca.delete()
    messages.success(request, f'Época "{nombre}" eliminada.')
    return redirect('home')


# ── Admin: eventos ────────────────────────────────────────────────────────────

@require_POST
def editar_evento(request, slug, evento_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca  = get_object_or_404(Epoca, slug=slug)
    evento = get_object_or_404(Evento, pk=evento_id, epoca=epoca)
    form   = EventoForm(request.POST, instance=evento)
    if form.is_valid():
        form.save()
        messages.success(request, f'"{evento.titulo}" actualizado.')
    else:
        messages.error(request, 'Error al guardar.')
    return redirect('detalle_evento', slug=slug, evento_id=evento_id)


def crear_evento(request, slug):
    """
    Crea un nuevo evento dentro de una época.
    Un evento es cada capítulo o hecho histórico, ej. 'El Atentado de Sarajevo'.
    También guarda los puntos del mapa enviados como JSON en 'puntos_mapa_json'.
    """
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')

    epoca = get_object_or_404(Epoca, slug=slug)

    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento       = form.save(commit=False)
            evento.epoca = epoca
            evento.save()

            # ── Guardar puntos del mapa ──────────────────
            import json as _json
            puntos_raw = request.POST.get('puntos_mapa_json', '[]')
            try:
                puntos = _json.loads(puntos_raw)
            except ValueError:
                puntos = []

            for p in puntos:
                try:
                    from .models import PuntoMapa
                    PuntoMapa.objects.create(
                        evento      = evento,
                        nombre      = str(p.get('nombre', ''))[:200],
                        descripcion = str(p.get('descripcion', '')),
                        tipo        = str(p.get('tipo', 'otro')),
                        bando       = str(p.get('bando', 'neutral')),
                        latitud     = float(p.get('lat', 0)),
                        longitud    = float(p.get('lng', 0)),
                    )
                except (KeyError, ValueError, TypeError):
                    pass  # ignorar puntos malformados

            messages.success(request, f'Evento "{evento.titulo}" creado.')
            return redirect('detalle_evento', slug=slug, evento_id=evento.pk)
        else:
            messages.error(request, 'Error al crear el evento.')
    else:
        form = EventoForm()

    return render(request, 'crear_evento.html', {
        'form':  form,
        'epoca': epoca,
        **_ctx(request),
    })


@require_POST
def eliminar_evento(request, slug, evento_id):
    """Elimina un evento y todos sus materiales."""
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca  = get_object_or_404(Epoca, slug=slug)
    evento = get_object_or_404(Evento, pk=evento_id, epoca=epoca)
    evento.delete()
    messages.success(request, 'Evento eliminado.')
    return redirect('detalle_epoca', slug=slug)


# ── Admin: países ─────────────────────────────────────────────────────────────

@require_POST
def editar_pais(request, slug, pais_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca = get_object_or_404(Epoca, slug=slug)
    pais  = get_object_or_404(Pais, pk=pais_id, epoca=epoca)
    form  = PaisForm(request.POST, instance=pais)
    if form.is_valid():
        form.save()
        messages.success(request, f'"{pais.nombre}" actualizado.')
    else:
        messages.error(request, 'Error al guardar.')
    return redirect('detalle_pais', slug=slug, pais_id=pais_id)


@require_POST
def crear_pais(request, slug):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca = get_object_or_404(Epoca, slug=slug)
    form  = PaisForm(request.POST)
    if form.is_valid():
        pais       = form.save(commit=False)
        pais.epoca = epoca
        pais.save()
        messages.success(request, f'País "{pais.nombre}" creado.')
    else:
        messages.error(request, 'Error al crear el país. Revisa los campos.')
    return redirect('detalle_epoca', slug=slug)


@require_POST
def eliminar_pais(request, slug, pais_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca  = get_object_or_404(Epoca, slug=slug)
    pais   = get_object_or_404(Pais, pk=pais_id, epoca=epoca)
    nombre = pais.nombre
    pais.delete()
    messages.success(request, f'País "{nombre}" eliminado.')
    return redirect('detalle_epoca', slug=slug)


# ── Admin: materiales ─────────────────────────────────────────────────────────

@require_POST
def agregar_material(request, slug, evento_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca  = get_object_or_404(Epoca, slug=slug)
    evento = get_object_or_404(Evento, pk=evento_id, epoca=epoca)
    form   = MaterialForm(request.POST, request.FILES)
    if form.is_valid():
        mat        = form.save(commit=False)
        mat.evento = evento
        if request.FILES.get('archivo'):
            from .supabase_storage import subir_archivo
            mat.archivo = subir_archivo(request.FILES['archivo'], 'eventos')
        if mat.todos_los_grados:
            mat.save()
            mat.grados.clear()
        else:
            mat.save()
            form.save_m2m()
        messages.success(request, 'Material agregado.')
    else:
        messages.error(request, f'Error al subir el material: {form.errors}')
    return redirect('detalle_evento', slug=slug, evento_id=evento_id)


@require_POST
def eliminar_material(request, slug, evento_id, material_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    material = get_object_or_404(Material, pk=material_id, evento__id=evento_id)
    material.delete()
    messages.success(request, 'Material eliminado.')
    return redirect('detalle_evento', slug=slug, evento_id=evento_id)


@require_POST
def agregar_material_pais(request, slug, pais_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca = get_object_or_404(Epoca, slug=slug)
    pais  = get_object_or_404(Pais, pk=pais_id, epoca=epoca)
    form  = MaterialPaisForm(request.POST, request.FILES)
    if form.is_valid():
        mat      = form.save(commit=False)
        mat.pais = pais
        if request.FILES.get('archivo'):
            from .supabase_storage import subir_archivo
            mat.archivo = subir_archivo(request.FILES['archivo'], 'paises')
        if mat.todos_los_grados:
            mat.save()
            mat.grados.clear()
        else:
            mat.save()
            form.save_m2m()
        messages.success(request, 'Material agregado al país.')
    else:
        messages.error(request, f'Error al subir el material: {form.errors}')
    return redirect('detalle_pais', slug=slug, pais_id=pais_id)


@require_POST
def eliminar_material_pais(request, slug, pais_id, material_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    material = get_object_or_404(MaterialPais, pk=material_id, pais__id=pais_id)
    material.delete()
    messages.success(request, 'Material eliminado.')
    return redirect('detalle_pais', slug=slug, pais_id=pais_id)


@require_POST
def agregar_material_epoca(request, slug):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca = get_object_or_404(Epoca, slug=slug)
    form  = MaterialEpocaForm(request.POST, request.FILES)
    if form.is_valid():
        mat       = form.save(commit=False)
        mat.epoca = epoca
        if request.FILES.get('archivo'):
            from .supabase_storage import subir_archivo
            mat.archivo = subir_archivo(request.FILES['archivo'], 'epocas')
        if mat.todos_los_grados:
            mat.save()
            mat.grados.clear()
        else:
            mat.save()
            form.save_m2m()
        messages.success(request, 'Material agregado a la época.')
    else:
        messages.error(request, f'Error al subir el material: {form.errors}')
    return redirect('detalle_epoca', slug=slug)

@require_POST
def eliminar_material_epoca(request, slug, material_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    material = get_object_or_404(MaterialEpoca, pk=material_id, epoca__slug=slug)
    material.delete()
    messages.success(request, 'Material eliminado.')
    return redirect('detalle_epoca', slug=slug)

    # ── Pega esto al final de epocas/views.py ──────────────────────────────────

from .ia_service import generar_evento as ia_generar_evento
from .models import PuntoMapa, ZonaMapa, LineaMapa

def generar_evento_ia(request, slug):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')

    epoca = get_object_or_404(Epoca, slug=slug)

    if request.method == 'GET':
        return render(request, 'generar_evento_ia.html', {
            'epoca': epoca,
            **_ctx(request),
        })

    # POST — recibir datos y llamar a Groq
    titulo = request.POST.get('titulo', '').strip()
    anio   = request.POST.get('anio', '').strip()
    mes    = request.POST.get('mes', '').strip() or None

    if not titulo or not anio:
        messages.error(request, 'El título y el año son obligatorios.')
        return render(request, 'generar_evento_ia.html', {
            'epoca': epoca, **_ctx(request),
        })

    try:
        datos = ia_generar_evento(titulo, anio, epoca.nombre, mes)

        # Crear el evento
        from .forms import EventoForm
        evento = Evento.objects.create(
            epoca       = epoca,
            titulo      = datos.get('titulo', titulo),
            anio        = datos.get('anio', int(anio)),
            mes         = datos.get('mes') or None,
            icono       = datos.get('icono', '📖'),
            resumen     = datos.get('resumen', '')[:300],
            descripcion = datos.get('descripcion', ''),
            orden       = Evento.objects.filter(epoca=epoca).count() + 1,
        )

        # Crear puntos del mapa
        for i, p in enumerate(datos.get('puntos_mapa', [])):
            PuntoMapa.objects.create(
                evento      = evento,
                nombre      = str(p.get('nombre', ''))[:200],
                descripcion = str(p.get('descripcion', '')),
                tipo        = p.get('tipo', 'otro'),
                bando       = p.get('bando', 'neutral'),
                latitud     = float(p.get('latitud', 0)),
                longitud    = float(p.get('longitud', 0)),
                orden       = p.get('orden', i),
            )

        # Crear zonas del mapa
        for i, z in enumerate(datos.get('zonas_mapa', [])):
            ZonaMapa.objects.create(
                evento      = evento,
                nombre      = str(z.get('nombre', ''))[:200],
                descripcion = str(z.get('descripcion', '')),
                bando       = z.get('bando', 'neutral'),
                coordenadas = z.get('coordenadas', []),
                orden       = z.get('orden', i),
            )

        # Crear líneas del mapa
        for i, l in enumerate(datos.get('lineas_mapa', [])):
            LineaMapa.objects.create(
                evento      = evento,
                nombre      = str(l.get('nombre', ''))[:200],
                descripcion = str(l.get('descripcion', '')),
                tipo        = l.get('tipo', 'otro'),
                bando       = l.get('bando', 'neutral'),
                coordenadas = l.get('coordenadas', []),
                orden       = l.get('orden', i),
            )

        messages.success(request, '✅ Evento generado con IA. Revisa y edita lo que necesites.')
        return redirect('detalle_evento', slug=slug, evento_id=evento.pk)

    except Exception as e:
        messages.error(request, f'Error al generar con IA: {e}')
        return render(request, 'generar_evento_ia.html', {
            'epoca': epoca, **_ctx(request),
        })

import requests as req_lib
from django.http import HttpResponse
import mimetypes

def proxy_material(request, modelo, pk):
    if not _check_sesion(request):
        return redirect('login')
    from .models import Material, MaterialPais, MaterialEpoca
    modelos = {'evento': Material, 'pais': MaterialPais, 'epoca': MaterialEpoca}
    obj = get_object_or_404(modelos[modelo], pk=pk)
    url = str(obj.archivo) if obj.archivo else obj.url
    return redirect(url)