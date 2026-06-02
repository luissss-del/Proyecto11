from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from .models import user, login as LoginModel
from .forms import userForm
from django.core.mail import send_mail
from django.conf import settings
from .models import TokenRecuperacion
from epocas.models import Epoca


def index(request):
    form = userForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = userForm(request.POST)
        if form.is_valid():
            nuevo_usuario = form.save()
            LoginModel.objects.create(
                nombre=nuevo_usuario,
                password=nuevo_usuario
            )
            messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión.')
            return redirect('login')
        else:
            return render(request, 'login.html', {'form': form})
    return redirect('index')


def login_view(request):
    if request.method == 'POST':
        ti_ingresado       = request.POST.get('Ti', '').strip()
        password_ingresado = request.POST.get('password', '').strip()

        if not ti_ingresado.isdigit():
            messages.error(request, 'Ingresa un número de identificación válido.')
            return render(request, 'login.html', {'form': userForm()})

        try:
            usuario = user.objects.get(Ti=int(ti_ingresado))
        except user.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese número de identificación.')
            return render(request, 'login.html', {'form': userForm()})

        if usuario.password != password_ingresado:
            messages.error(request, 'Contraseña incorrecta.')
            return render(request, 'login.html', {'form': userForm()})

        existe_login = LoginModel.objects.filter(
            nombre=usuario, password=usuario
        ).exists()

        if not existe_login:
            messages.error(request, 'No tienes permiso de acceso.')
            return render(request, 'login.html', {'form': userForm()})

        # NO actualizamos ultimo_acceso en el login.
        # El heartbeat lo hace cada 30 s mientras la pestaña está abierta.
        request.session['usuario_id']     = usuario.pk
        request.session['usuario_nombre'] = usuario.nombre
        request.session['es_admin']       = usuario.es_admin
        request.session.modified = True

        return redirect('home')

    return render(request, 'login.html', {'form': userForm()})


def home(request):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    nombre   = request.session.get('usuario_nombre', 'Estudiante')
    es_admin = request.session.get('es_admin', False)
    epocas   = Epoca.objects.all().order_by('orden', 'anio_inicio')

    return render(request, 'home.html', {
        'nombre':   nombre,
        'es_admin': es_admin,
        'epocas':   epocas,
    })


# ── Heartbeat ─────────────────────────────────────────────────────────────────
@require_POST
def heartbeat(request):
    uid = request.session.get('usuario_id')
    if not uid:
        return JsonResponse({'ok': False}, status=401)
    try:
        u = user.objects.get(pk=uid)
        u.ultimo_acceso = timezone.now()
        u.save(update_fields=['ultimo_acceso'])
        return JsonResponse({'ok': True})
    except user.DoesNotExist:
        return JsonResponse({'ok': False}, status=404)


# ── API JSON estudiantes ──────────────────────────────────────────────────────
@require_GET
def api_estudiantes(request):
    if not request.session.get('es_admin'):
        return JsonResponse({'error': 'Sin permiso'}, status=403)

    ahora = timezone.now()
    lista = user.objects.filter(es_admin=False).select_related('grado').order_by('grado__orden', 'apellido')

    data = []
    for est in lista:
        if est.ultimo_acceso:
            seg = (ahora - est.ultimo_acceso).total_seconds()
            if seg < 90:
                estado, ultimo = 'conectado', 'En línea ahora'
            elif seg < 3600:
                estado, ultimo = 'reciente', f'Hace {int(seg//60)} min'
            elif seg < 86400:
                estado, ultimo = 'hoy', f'Hace {int(seg//3600)} h'
            else:
                d = int(seg // 86400)
                estado, ultimo = 'inactivo', f'Hace {d} día{"s" if d != 1 else ""}'
        else:
            estado, ultimo = 'nunca', 'Nunca'

        data.append({
            'id': est.pk, 'nombre': est.nombre, 'apellido': est.apellido,
            'correo': est.correo, 'grado': est.grado.nombre if est.grado else '—',
            'estado': estado, 'ultimo': ultimo,
        })

    return JsonResponse({'estudiantes': data})


def eliminar_estudiante(request, estudiante_id):
    if not request.session.get('usuario_id') or not request.session.get('es_admin'):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    if request.method == 'POST':
        try:
            est = user.objects.get(pk=estudiante_id, es_admin=False)
            est.delete()
            messages.success(request, 'Estudiante eliminado correctamente.')
        except user.DoesNotExist:
            messages.error(request, 'Estudiante no encontrado.')
    return redirect('home')


def logout_view(request):
    uid = request.session.get('usuario_id')
    if uid:
        try:
            u = user.objects.get(pk=uid)
            u.ultimo_acceso = None
            u.save(update_fields=['ultimo_acceso'])
        except user.DoesNotExist:
            pass
    request.session.flush()
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')

import threading

def _enviar_correo(usuario, link):
    send_mail(
        subject='WorldLearn — Recuperación de contraseña',
        message=f'Hola {usuario.nombre},\n\nHaz clic en el siguiente enlace para restablecer tu contraseña. El link es válido por 1 hora:\n\n{link}\n\nSi no solicitaste esto, ignora este correo.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[usuario.correo],
        fail_silently=True,
    )

def recuperar_password(request):
    if request.method == 'POST':
        ti = request.POST.get('ti', '').strip()
        try:
            if not ti.isdigit():
                return render(request, 'recuperar_password.html', {'error': 'Ingresa un número de identificación válido.'})
            usuario = user.objects.filter(Ti=int(ti)).first()
            if not usuario:
                return render(request, 'recuperar_password.html', {'error': 'No existe una cuenta con ese número de identificación.'})
            if not usuario.correo:
                return render(request, 'recuperar_password.html', {'error': 'Esta cuenta no tiene un correo registrado. Contacta al profesor.'})
            token = TokenRecuperacion.objects.create(usuario=usuario)
            dominio = request.build_absolute_uri('/').rstrip('/')
            link = f"{dominio}/reset/{token.token}/"
            threading.Thread(target=_enviar_correo, args=(usuario, link), daemon=True).start()
            return render(request, 'recuperar_password.html', {'enviado': True})
        except Exception as e:
            return render(request, 'recuperar_password.html', {'error': f'Error: {str(e)}'})
    return render(request, 'recuperar_password.html', {})


def reset_password(request, token):
    try:
        tok = TokenRecuperacion.objects.get(token=token)
    except TokenRecuperacion.DoesNotExist:
        return render(request, 'reset_password.html', {'error': 'El enlace no es válido.'})

    if not tok.esta_vigente():
        return render(request, 'reset_password.html', {'error': 'El enlace ha expirado. Solicita uno nuevo.'})

    if request.method == 'POST':
        nueva     = request.POST.get('password', '')
        confirmar = request.POST.get('confirmar', '')
        if len(nueva) < 6:
            return render(request, 'reset_password.html', {'token': token, 'error': 'La contraseña debe tener al menos 6 caracteres.'})
        if nueva != confirmar:
            return render(request, 'reset_password.html', {'token': token, 'error': 'Las contraseñas no coinciden.'})
        tok.usuario.password = nueva
        tok.usuario.save()
        tok.usado = True
        tok.save()
        return render(request, 'reset_password.html', {'exito': True})

    return render(request, 'reset_password.html', {'token': token})


def editar_perfil(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    from .models import Grado
    usuario_id  = request.session.get('usuario_id')
    usuario_obj = user.objects.get(pk=usuario_id)
    grados      = Grado.objects.all()

    ctx = {
        'nombre':   request.session.get('usuario_nombre', ''),
        'es_admin': request.session.get('es_admin', False),
        'grados':   grados,
    }

    if request.method == 'GET':
        request.session['perfil_next'] = request.META.get('HTTP_REFERER', '/')

    if request.method == 'POST':
        nombre    = request.POST.get('nombre', '').strip()
        apellido  = request.POST.get('apellido', '').strip()
        correo    = request.POST.get('correo', '').strip()
        password  = request.POST.get('password', '').strip()
        confirmar = request.POST.get('confirmar', '').strip()
        grado_id  = request.POST.get('grado') or None

        if not nombre or not apellido or not correo:
            return render(request, 'editar_perfil.html', {'usuario': usuario_obj, 'error': 'Nombre, apellido y correo son obligatorios.', **ctx})
        if password and password != confirmar:
            return render(request, 'editar_perfil.html', {'usuario': usuario_obj, 'error': 'Las contraseñas no coinciden.', **ctx})
        if password and len(password) < 6:
            return render(request, 'editar_perfil.html', {'usuario': usuario_obj, 'error': 'La contraseña debe tener al menos 6 caracteres.', **ctx})

        usuario_obj.nombre   = nombre
        usuario_obj.apellido = apellido
        usuario_obj.correo   = correo
        usuario_obj.grado_id = grado_id
        if password:
            usuario_obj.password = password
        usuario_obj.save()

        request.session['usuario_nombre'] = nombre
        request.session.modified = True

        next_url = request.session.pop('perfil_next', '/')
        return redirect(next_url)

    return render(request, 'editar_perfil.html', {'usuario': usuario_obj, **ctx})