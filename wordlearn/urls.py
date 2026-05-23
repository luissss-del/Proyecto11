from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from login  import views as login_views
from epocas import views as epocas_views
from paises import views as paises_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Login / sesión ────────────────────────────────
    path('',          login_views.index,       name='index'),
    path('register/', login_views.register,    name='register'),
    path('login/',    login_views.login_view,  name='login'),
    path('home/',     login_views.home,        name='home'),
    path('logout/',   login_views.logout_view, name='logout'),
    path('perfil/editar/', login_views.editar_perfil, name='editar_perfil'),
    path('recuperar/', login_views.recuperar_password, name='recuperar_password'),
    path('reset/<uuid:token>/', login_views.reset_password, name='reset_password'),
    path('estudiante/<int:estudiante_id>/eliminar/', login_views.eliminar_estudiante, name='eliminar_estudiante'),

    # ── API ───────────────────────────────────────────
    path('api/heartbeat/',   login_views.heartbeat,       name='heartbeat'),
    path('api/estudiantes/', login_views.api_estudiantes, name='api_estudiantes'),

    # ── CRUD de Épocas ────────────────────────────────
    path('epoca/nueva/',
         epocas_views.crear_epoca,   name='crear_epoca'),
    path('epoca/<str:slug>/editar/',
         epocas_views.editar_epoca,  name='editar_epoca'),
    path('epoca/<str:slug>/eliminar/',
         epocas_views.eliminar_epoca, name='eliminar_epoca'),

    # ── Detalle de época ──────────────────────────────
    path('epoca/<str:slug>/',
         epocas_views.detalle_epoca,  name='detalle_epoca'),
         
     path('epoca/generar-ia/',
     epocas_views.generar_epoca_ia, name='generar_epoca_ia'),

    # ── Eventos ───────────────────────────────────────
    path('epoca/<str:slug>/evento/nuevo/',
         epocas_views.crear_evento,   name='crear_evento'),
    path('epoca/<str:slug>/evento/<int:evento_id>/',
         epocas_views.detalle_evento, name='detalle_evento'),
    path('epoca/<str:slug>/evento/<int:evento_id>/editar/',
         epocas_views.editar_evento,  name='editar_evento'),
    path('epoca/<str:slug>/evento/<int:evento_id>/eliminar/',
         epocas_views.eliminar_evento, name='eliminar_evento'),
    path('epoca/<str:slug>/evento/<int:evento_id>/material/agregar/',
         epocas_views.agregar_material, name='agregar_material'),
    path('epoca/<str:slug>/evento/<int:evento_id>/material/<int:material_id>/eliminar/',
         epocas_views.eliminar_material, name='eliminar_material'),
    path('epoca/<str:slug>/evento/generar-ia/',
         epocas_views.generar_evento_ia, name='generar_evento_ia'),

    # ── Países dentro de época ────────────────────────
    path('epoca/<str:slug>/pais/<int:pais_id>/',
         epocas_views.detalle_pais,   name='detalle_pais'),
    path('epoca/<str:slug>/material/agregar/',
         epocas_views.agregar_material_epoca, name='agregar_material_epoca'),
    path('epoca/<str:slug>/material/<int:material_id>/eliminar/',
         epocas_views.eliminar_material_epoca, name='eliminar_material_epoca'),
    path('epoca/<str:slug>/pais/crear/',
         epocas_views.crear_pais,     name='crear_pais'),
    path('epoca/<str:slug>/pais/<int:pais_id>/editar/',
         epocas_views.editar_pais,    name='editar_pais'),
    path('epoca/<str:slug>/pais/<int:pais_id>/eliminar/',
         epocas_views.eliminar_pais,  name='eliminar_pais'),
    path('epoca/<str:slug>/pais/<int:pais_id>/material/agregar/',
         epocas_views.agregar_material_pais, name='agregar_material_pais'),
    path('epoca/<str:slug>/pais/<int:pais_id>/material/<int:material_id>/eliminar/',
         epocas_views.eliminar_material_pais, name='eliminar_material_pais'),

    # ── Sección Países del mundo ──────────────────────
    path('paises/',
         paises_views.lista_continentes, name='lista_continentes'),
    path('paises/<str:continente_slug>/',
         paises_views.lista_paises, name='lista_paises'),
    path('paises/<str:continente_slug>/<str:pais_slug>/',
         paises_views.detalle_pais, name='detalle_pais_seccion'),
    path('paises/<str:continente_slug>/<str:pais_slug>/editar/',
         paises_views.editar_pais, name='editar_pais_seccion'),
    path('paises/<str:continente_slug>/<str:pais_slug>/ciudad/agregar/',
         paises_views.agregar_ciudad, name='agregar_ciudad'),
    path('paises/<str:continente_slug>/<str:pais_slug>/ciudad/<int:ciudad_id>/eliminar/',
         paises_views.eliminar_ciudad, name='eliminar_ciudad'),
    path('paises/<str:continente_slug>/<str:pais_slug>/material/agregar/',
         paises_views.agregar_material, name='agregar_material_pais_seccion'),
    path('paises/<str:continente_slug>/<str:pais_slug>/material/<int:material_id>/eliminar/',
         paises_views.eliminar_material, name='eliminar_material_pais_seccion'),
    path('material/<str:modelo>/<int:pk>/ver/',
         epocas_views.proxy_material, name='proxy_material'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)