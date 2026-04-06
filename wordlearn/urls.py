"""
URL configuration for wordlearn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from login  import views as login_views
from epocas import views as epocas_views
from paises import views as paises_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Login ─────────────────────────────────────────
    path('',          login_views.index,       name='index'),
    path('register/', login_views.register,    name='register'),
    path('login/',    login_views.login_view,  name='login'),
    path('home/',     login_views.home,        name='home'),
    path('logout/',   login_views.logout_view, name='logout'),
    path('perfil/editar/', login_views.editar_perfil, name='editar_perfil'),
    path('recuperar/', login_views.recuperar_password, name='recuperar_password'),
    path('reset/<uuid:token>/', login_views.reset_password, name='reset_password'),
    path('estudiante/<int:estudiante_id>/eliminar/', login_views.eliminar_estudiante, name='eliminar_estudiante'),

    # ── Épocas ────────────────────────────────────────
    path('epoca/<str:slug>/',
         epocas_views.detalle_epoca,  name='detalle_epoca'),
    path('epoca/<str:slug>/evento/<int:evento_id>/',
         epocas_views.detalle_evento, name='detalle_evento'),
    path('epoca/<str:slug>/pais/<int:pais_id>/',
         epocas_views.detalle_pais,   name='detalle_pais'),

    # ── Admin: eventos ────────────────────────────────
    path('epoca/<str:slug>/evento/<int:evento_id>/editar/',
         epocas_views.editar_evento, name='editar_evento'),
    path('epoca/<str:slug>/evento/<int:evento_id>/material/agregar/',
         epocas_views.agregar_material, name='agregar_material'),
    path('epoca/<str:slug>/evento/<int:evento_id>/material/<int:material_id>/eliminar/',
         epocas_views.eliminar_material, name='eliminar_material'),

    # ── Admin: países ─────────────────────────────────
    path('epoca/<str:slug>/material/agregar/',
         epocas_views.agregar_material_epoca, name='agregar_material_epoca'),
    path('epoca/<str:slug>/material/<int:material_id>/eliminar/',
         epocas_views.eliminar_material_epoca, name='eliminar_material_epoca'),
    path('epoca/<str:slug>/pais/crear/',
         epocas_views.crear_pais, name='crear_pais'),
    path('epoca/<str:slug>/pais/<int:pais_id>/editar/',
         epocas_views.editar_pais, name='editar_pais'),
    path('epoca/<str:slug>/pais/<int:pais_id>/eliminar/',
         epocas_views.eliminar_pais, name='eliminar_pais'),

    # ── Admin: materiales de países ───────────────────
    path('epoca/<str:slug>/pais/<int:pais_id>/material/agregar/',
         epocas_views.agregar_material_pais, name='agregar_material_pais'),
    path('epoca/<str:slug>/pais/<int:pais_id>/material/<int:material_id>/eliminar/',
         epocas_views.eliminar_material_pais, name='eliminar_material_pais'),

      path('paises/',
         paises_views.lista_continentes, name='lista_continentes'),
    path('paises/<str:continente_slug>/',
         paises_views.lista_paises, name='lista_paises'),
    path('paises/<str:continente_slug>/<str:pais_slug>/',
         paises_views.detalle_pais, name='detalle_pais_seccion'),

    # ── Admin sección Países ───────────────────────────────────
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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
