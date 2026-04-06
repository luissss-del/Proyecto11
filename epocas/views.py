from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Epoca, Evento, Pais, Material, MaterialPais
from .forms import EventoForm, PaisForm, MaterialForm, MaterialPaisForm, MaterialEpocaForm


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
    """Retorna el objeto Grado del usuario en sesión, o None si no tiene."""
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
    """
    Si es admin ve todo.
    Si el estudiante tiene grado: ve materiales de todos_los_grados=True
    o donde su grado esté en la lista de grados.
    Si no tiene grado: solo ve los de todos_los_grados=True.
    """
    if es_admin:
        return queryset
    if grado_usuario:
        from django.db.models import Q
        return queryset.filter(
            Q(todos_los_grados=True) | Q(grados=grado_usuario)
        ).distinct()
    return queryset.filter(todos_los_grados=True)


def detalle_epoca(request, slug):
    if not _check_sesion(request):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    es_admin      = _check_admin(request)
    grado_usuario = _get_grado_usuario(request)

    epoca       = get_object_or_404(Epoca, slug=slug)
    eventos     = list(epoca.eventos.all())
    principales = list(epoca.paises.filter(tipo='principal'))
    colaterales = list(epoca.paises.filter(tipo='colateral'))

    # Filtrar materiales de la época según grado
    materiales_epoca = _filtrar_materiales(
        epoca.materiales_epoca.all(), grado_usuario, es_admin
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

    epoca  = get_object_or_404(Epoca, slug=slug)
    evento = get_object_or_404(Evento, pk=evento_id, epoca=epoca)

    todos   = list(epoca.eventos.all())
    idx     = next((i for i, e in enumerate(todos) if e.pk == evento.pk), None)
    prev_ev = todos[idx - 1] if idx and idx > 0                       else None
    next_ev = todos[idx + 1] if idx is not None and idx < len(todos)-1 else None

    # Filtrar materiales del evento según grado
    materiales = _filtrar_materiales(
        evento.materiales.all(), grado_usuario, es_admin
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

    epoca = get_object_or_404(Epoca, slug=slug)
    pais  = get_object_or_404(Pais, pk=pais_id, epoca=epoca)

    # Filtrar materiales del país según grado
    materiales = _filtrar_materiales(
        pais.materiales.all(), grado_usuario, es_admin
    )

    return render(request, 'detalle_pais.html', {
        'epoca':             epoca,
        'pais':              pais,
        'materiales':        materiales,
        'form_pais':         PaisForm(instance=pais),
        'form_material_pais': MaterialPaisForm(),
        'grado_usuario':     grado_usuario,
        **_ctx(request),
    })


# ── Solo admin ────────────────────────────────────────────────────────────────

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
        mat.save()
        form.save_m2m()  # Guardar relación ManyToMany de grados
        messages.success(request, 'Material agregado.')
    else:
        messages.error(request, 'Error al subir el material.')
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
        mat.save()
        form.save_m2m()  # Guardar relación ManyToMany de grados
        messages.success(request, 'Material agregado al país.')
    else:
        messages.error(request, 'Error al subir el material.')
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
        mat.save()
        form.save_m2m()  # Guardar relación ManyToMany de grados
        messages.success(request, 'Material agregado a la época.')
    else:
        messages.error(request, 'Error al subir el material.')
    return redirect('detalle_epoca', slug=slug)


@require_POST
def eliminar_material_epoca(request, slug, material_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    from .models import MaterialEpoca
    material = get_object_or_404(MaterialEpoca, pk=material_id, epoca__slug=slug)
    material.delete()
    messages.success(request, 'Material eliminado.')
    return redirect('detalle_epoca', slug=slug)



def detalle_epoca(request, slug):
    if not _check_sesion(request):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    epoca       = get_object_or_404(Epoca, slug=slug)
    eventos     = list(epoca.eventos.all())
    principales = list(epoca.paises.filter(tipo='principal'))
    colaterales = list(epoca.paises.filter(tipo='colateral'))

    return render(request, 'detalle_epoca.html', {
        'epoca':              epoca,
        'eventos':            eventos,
        'principales':        principales,
        'colaterales':        colaterales,
        'form_nuevo_pais':    PaisForm(),
        'form_material_epoca': MaterialEpocaForm(),
        **_ctx(request),
    })


def detalle_evento(request, slug, evento_id):
    if not _check_sesion(request):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    epoca  = get_object_or_404(Epoca, slug=slug)
    evento = get_object_or_404(Evento, pk=evento_id, epoca=epoca)

    todos   = list(epoca.eventos.all())
    idx     = next((i for i, e in enumerate(todos) if e.pk == evento.pk), None)
    prev_ev = todos[idx - 1] if idx and idx > 0                      else None
    next_ev = todos[idx + 1] if idx is not None and idx < len(todos)-1 else None

    return render(request, 'detalle_evento.html', {
        'epoca':            epoca,
        'evento':           evento,
        'evento_anterior':  prev_ev,
        'evento_siguiente': next_ev,
        'form_evento':      EventoForm(instance=evento),
        'form_material':    MaterialForm(),
        **_ctx(request),
    })


def detalle_pais(request, slug, pais_id):
    if not _check_sesion(request):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    epoca = get_object_or_404(Epoca, slug=slug)
    pais  = get_object_or_404(Pais, pk=pais_id, epoca=epoca)

    return render(request, 'detalle_pais.html', {
        'epoca':     epoca,
        'pais':      pais,
        'form_pais': PaisForm(instance=pais),
        **_ctx(request),
    })


# ── Solo admin ────────────────────────────────────────────────────────────────

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


@require_POST
def agregar_material(request, slug, evento_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    epoca  = get_object_or_404(Epoca, slug=slug)
    evento = get_object_or_404(Evento, pk=evento_id, epoca=epoca)
    form   = MaterialForm(request.POST, request.FILES)
    if form.is_valid():
        mat = form.save(commit=False)
        mat.evento = evento
        mat.save()
        messages.success(request, 'Material agregado.')
    else:
        messages.error(request, 'Error al subir el material.')
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
        mat.save()
        messages.success(request, 'Material agregado al país.')
    else:
        messages.error(request, 'Error al subir el material.')
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
        mat.save()
        messages.success(request, 'Material agregado a la época.')
    else:
        messages.error(request, 'Error al subir el material.')
    return redirect('detalle_epoca', slug=slug)


@require_POST
def eliminar_material_epoca(request, slug, material_id):
    if not _check_admin(request):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    from .models import MaterialEpoca
    material = get_object_or_404(MaterialEpoca, pk=material_id, epoca__slug=slug)
    material.delete()
    messages.success(request, 'Material eliminado.')
    return redirect('detalle_epoca', slug=slug)