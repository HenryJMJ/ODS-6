from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import unirse_o_salir_proyecto

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('panel/notificaciones/', views.notificaciones_admin, name='notificaciones_admin'),
    path('proyectos/crear/', views.crear_proyecto, name='crear_proyecto'),
    path('proyecto/<int:proyecto_id>/editar/', views.editar_proyecto, name='editar_proyecto'),
    path('proyecto/<int:proyecto_id>/eliminar/', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('proyectos/comunidad/<int:proyecto_id>/', views.proyecto_comunidad, name='proyecto_comunidad'),
    path('marcar-leido/<int:mensaje_id>/', views.marcar_mensaje_leido, name='marcar_mensaje_leido'),
    path('marcar_usuario_leido/<int:user_id>/', views.marcar_usuario_leido, name='marcar_usuario_leido'),
    path('usuarios/', views.usuarios_registrados, name='usuarios_registrados'),
    path('mensajes/', views.mensajes, name='mensajes'),
    path('admin-panel/responder/<int:mensaje_id>/', views.responder_mensaje, name='responder_mensaje'),
    path('admin-panel/eliminar/<int:mensaje_id>/', views.eliminar_mensaje, name='eliminar_mensaje'),
    path('ajustes/', views.panel_ajustes, name='panel_ajustes'),
    path('panel-usuario/', views.panel_usuario, name='panel_usuario'),
    path('mis-mensajes/', views.mis_mensajes, name='mis_mensajes'),
    path('contacto-usuario/', views.contacto_usuario, name='contacto_usuario'),
    path('usuario/ajustes/', views.ajustes_usuario, name='ajustes_usuario'),
    path('usuario/proyectos/', views.proyectos_disponibles, name='proyectos_disponibles'),
    path('proyectos/unirse_o_salir/<int:proyecto_id>/', unirse_o_salir_proyecto, name='unirse_o_salir_proyecto'),
    path('proyectos/comunidad/usuario/<int:proyecto_id>/', views.proyecto_comunidad_usuario, name='proyecto_comunidad_usuario'),
    path('proyecto/<int:proyecto_id>/idea/<int:idea_id>/editar/', views.editar_idea, name='editar_idea'),
    path('proyecto/<int:proyecto_id>/idea/<int:idea_id>/eliminar/', views.eliminar_idea, name='eliminar_idea'),
    path('proyecto/<int:proyecto_id>/idea/<int:idea_id>/marcar-me-gusta/', views.marcar_me_gusta, name='marcar_me_gusta'),
    path('', views.index, name='index'),
    path('que-es/', views.que_es, name='que_es'),
    path('solucion/', views.solucion, name='solucion'),
    path('ayudar/', views.ayudar, name='ayudar'),
    path('contacto/', views.contacto, name='contacto'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)