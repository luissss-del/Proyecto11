from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Continente, Region, Pais, CiudadPais, MaterialPaisSeccion
from .forms import PaisForm, CiudadPaisForm, MaterialPaisSeccionForm


def _check_sesion(request):
    return bool(request.session.get('usuario_id'))

def _check_admin(request):
    return request.session.get('es_admin') == True

def _ctx(request):
    return {
        'nombre':   request.session.get('usuario_nombre', 'Estudiante'),
        'es_admin': request.session.get('es_admin', False),
    }


def lista_continentes(request):
    if not _check_sesion(request):
        return redirect('login')
    continentes = Continente.objects.prefetch_related('regiones__paises')
    return render(request, 'lista_continentes.html', {
        'continentes': continentes,
        **_ctx(request),
    })


def lista_paises(request, continente_slug):
    if not _check_sesion(request):
        return redirect('login')
    continente = get_object_or_404(Continente, slug=continente_slug)
    regiones   = continente.regiones.prefetch_related('paises').all()
    return render(request, 'lista_paises.html', {
        'continente': continente,
        'regiones':   regiones,
        **_ctx(request),
    })


def detalle_pais(request, continente_slug, pais_slug):
    if not _check_sesion(request):
        return redirect('login')
    continente = get_object_or_404(Continente, slug=continente_slug)
    pais       = get_object_or_404(Pais, slug=pais_slug, region__continente=continente)
    ciudades   = pais.ciudades.all()
    materiales = pais.materiales.all()
    return render(request, 'detalle_pais_seccion.html', {
        'continente': continente,
        'pais':       pais,
        'ciudades':   ciudades,
        'materiales': materiales,
        'form_pais':  PaisForm(instance=pais),
        'form_ciudad':   CiudadPaisForm(),
        'form_material': MaterialPaisSeccionForm(),
        **_ctx(request),
    })


# ── Admin ─────────────────────────────────────────────────────────────

@require_POST
def editar_pais(request, continente_slug, pais_slug):
    if not _check_admin(request):
        return redirect('login')
    continente = get_object_or_404(Continente, slug=continente_slug)
    pais       = get_object_or_404(Pais, slug=pais_slug, region__continente=continente)
    form       = PaisForm(request.POST, instance=pais)
    if form.is_valid():
        form.save()
        messages.success(request, f'"{pais.nombre}" actualizado.')
    else:
        messages.error(request, 'Error al guardar.')
    return redirect('detalle_pais_seccion', continente_slug=continente_slug, pais_slug=pais_slug)


@require_POST
def agregar_ciudad(request, continente_slug, pais_slug):
    if not _check_admin(request):
        return redirect('login')
    continente = get_object_or_404(Continente, slug=continente_slug)
    pais       = get_object_or_404(Pais, slug=pais_slug, region__continente=continente)
    form       = CiudadPaisForm(request.POST)
    if form.is_valid():
        ciudad      = form.save(commit=False)
        ciudad.pais = pais
        ciudad.save()
        messages.success(request, f'Ciudad "{ciudad.nombre}" agregada.')
    else:
        messages.error(request, 'Error al agregar ciudad.')
    return redirect('detalle_pais_seccion', continente_slug=continente_slug, pais_slug=pais_slug)


@require_POST
def eliminar_ciudad(request, continente_slug, pais_slug, ciudad_id):
    if not _check_admin(request):
        return redirect('login')
    ciudad = get_object_or_404(CiudadPais, pk=ciudad_id, pais__slug=pais_slug)
    ciudad.delete()
    messages.success(request, 'Ciudad eliminada.')
    return redirect('detalle_pais_seccion', continente_slug=continente_slug, pais_slug=pais_slug)


@require_POST
def agregar_material(request, continente_slug, pais_slug):
    if not _check_admin(request):
        return redirect('login')
    continente = get_object_or_404(Continente, slug=continente_slug)
    pais       = get_object_or_404(Pais, slug=pais_slug, region__continente=continente)
    form       = MaterialPaisSeccionForm(request.POST, request.FILES)
    if form.is_valid():
        mat      = form.save(commit=False)
        mat.pais = pais
        mat.save()
        messages.success(request, 'Material agregado.')
    else:
        messages.error(request, 'Error al subir el material.')
    return redirect('detalle_pais_seccion', continente_slug=continente_slug, pais_slug=pais_slug)


@require_POST
def eliminar_material(request, continente_slug, pais_slug, material_id):
    if not _check_admin(request):
        return redirect('login')
    material = get_object_or_404(MaterialPaisSeccion, pk=material_id, pais__slug=pais_slug)
    material.delete()
    messages.success(request, 'Material eliminado.')
    return redirect('detalle_pais_seccion', continente_slug=continente_slug, pais_slug=pais_slug)

