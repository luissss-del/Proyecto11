from django.shortcuts import render, redirect
from django.contrib import messages
from .models import user, login as LoginModel
from .forms import userForm
from django.core.mail import send_mail
from django.conf import settings
from .models import TokenRecuperacion


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
        nombre_ingresado   = request.POST.get('nombre', '').strip()
        password_ingresado = request.POST.get('password', '').strip()

        try:
            usuario = user.objects.get(nombre=nombre_ingresado)
        except user.DoesNotExist:
            messages.error(request, 'El usuario no existe.')
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

        # Guardar sesión — incluyendo si es admin/profesor
        request.session['usuario_id']     = usuario.pk
        request.session['usuario_nombre'] = usuario.nombre
        request.session['es_admin']       = usuario.es_admin  # ← nuevo
        request.session.modified = True  # Asegura que se guarde la sesión
        return redirect('home')

    return render(request, 'login.html', {'form': userForm()})


def home(request):
    if not request.session.get('usuario_id'):
        messages.error(request, 'Debes iniciar sesión primero.')
        return redirect('login')

    nombre   = request.session.get('usuario_nombre', 'Estudiante')
    es_admin = request.session.get('es_admin', False)

    estudiantes = []
    if es_admin:
        estudiantes = user.objects.filter(es_admin=False).select_related('grado').order_by('grado__orden', 'apellido')

    return render(request, 'home.html', {
        'nombre': nombre,
        'es_admin': es_admin,
        'estudiantes': estudiantes,
    })


def eliminar_estudiante(request, estudiante_id):
    if not request.session.get('usuario_id') or not request.session.get('es_admin'):
        messages.error(request, 'Sin permiso.')
        return redirect('login')
    if request.method == 'POST':
        try:
            est = user.objects.get(pk=estudiante_id, es_admin=False)
            est.delete()
            messages.success(request, f'Estudiante eliminado correctamente.')
        except user.DoesNotExist:
            messages.error(request, 'Estudiante no encontrado.')
    return redirect('home')


def logout_view(request):
    request.session.flush()
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')

def recuperar_password(request):
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        try:
            usuario = user.objects.filter(correo=correo).first()
            if not usuario:
                return render(request, 'recuperar_password.html', {'error': 'No existe una cuenta con ese correo.'})
            token = TokenRecuperacion.objects.create(usuario=usuario)
            link = f"http://127.0.0.1:8000/reset/{token.token}/"
            send_mail(
                subject='WorldLearn — Recuperación de contraseña',
                message=f'Hola {usuario.nombre},\n\nHaz clic en el siguiente enlace para restablecer tu contraseña. El link es válido por 1 hora:\n\n{link}\n\nSi no solicitaste esto, ignora este correo.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[correo],
            )
            return render(request, 'recuperar_password.html', {'enviado': True})
        except Exception as e:
            return render(request, 'recuperar_password.html', {'error': 'Ocurrió un error al enviar el correo. Intenta de nuevo.'})
    return render(request, 'recuperar_password.html', {})


def reset_password(request, token):
    try:
        tok = TokenRecuperacion.objects.get(token=token)
    except TokenRecuperacion.DoesNotExist:
        return render(request, 'reset_password.html', {'error': 'El enlace no es válido.'})

    if not tok.esta_vigente():
        return render(request, 'reset_password.html', {'error': 'El enlace ha expirado. Solicita uno nuevo.'})

    if request.method == 'POST':
        nueva = request.POST.get('password', '')
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

    # Guardar de dónde viene el usuario
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
            return render(request, 'editar_perfil.html', {
                'usuario': usuario_obj,
                'error': 'Nombre, apellido y correo son obligatorios.',
                **ctx,
            })

        if password and password != confirmar:
            return render(request, 'editar_perfil.html', {
                'usuario': usuario_obj,
                'error': 'Las contraseñas no coinciden.',
                **ctx,
            })

        if password and len(password) < 6:
            return render(request, 'editar_perfil.html', {
                'usuario': usuario_obj,
                'error': 'La contraseña debe tener al menos 6 caracteres.',
                **ctx,
            })

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

    return render(request, 'editar_perfil.html', {
        'usuario': usuario_obj,
        **ctx,
    })