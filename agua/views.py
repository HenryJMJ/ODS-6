from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.db.models import Count
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import update_session_auth_hash
from .services.news_service import obtener_noticias_ods6
from django.core.mail import EmailMessage
from .forms import AdminUpdateForm, AdminCambiarContrasenaForm
from .forms import ActualizarUsuarioForm, CambiarContrasenaForm
from django.conf import settings
from .forms import AdminUpdateForm
from .forms import RegistroForm
from .forms import LoginForm
from .models import MensajeContacto, UsuarioLeido
from .forms import ResponderMensajeForm
from .forms import ContactoForm
from .models import Proyecto
from .forms import ProyectoForm
from .models import Proyecto, IdeaUsuario
from .forms import IdeaUsuarioForm
from django.contrib import messages


#Administrador
def es_superusuario(user):
    return user.is_superuser

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    # Obtener las últimas noticias del ODS 6
    noticias = obtener_noticias_ods6()
    
    # Renderizar la plantilla y pasar las noticias como contexto
    return render(request, 'agua/admin_panel.html', {'noticias': noticias})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def notificaciones_admin(request):
    nuevos_usuarios = User.objects.order_by('-date_joined')[:10]
    mensajes = MensajeContacto.objects.order_by('-fecha')[:10]
    mensajes_no_respondidos = MensajeContacto.objects.filter(respondido=False).count()
    usuarios_no_leidos = UsuarioLeido.objects.filter(leido=False).count()

    # Calcular el total de notificaciones
    total_notificaciones = mensajes_no_respondidos + usuarios_no_leidos

    return render(request, 'agua/notificaciones_admin.html', {
        'nuevos_usuarios': nuevos_usuarios,
        'mensajes': mensajes,
        'mensajes_no_respondidos': mensajes_no_respondidos,
        'usuarios_no_leidos': usuarios_no_leidos,
        'total_notificaciones': total_notificaciones,  # Pasar el total de notificaciones
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def marcar_mensaje_leido(request, mensaje_id):
    mensaje = get_object_or_404(MensajeContacto, id=mensaje_id)
    mensaje.respondido = True
    mensaje.save()
    return redirect('notificaciones_admin') 

@login_required
@user_passes_test(lambda u: u.is_superuser)
def marcar_usuario_leido(request, user_id):
    usuario = User.objects.get(id=user_id)
    usuario_leido, created = UsuarioLeido.objects.get_or_create(user=usuario)
    usuario_leido.leido = True  # Marca como leído
    usuario_leido.save()
    return redirect('notificaciones_admin')

@login_required
@user_passes_test(lambda u: u.is_staff)
def crear_proyecto(request):
    if request.method == "POST":
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)  # No guarda aún el objeto en la base de datos
            proyecto.creado_por = request.user  # Asigna el usuario actual a "creado_por"
            proyecto.save()  # Guarda el proyecto con el usuario asignado
            return redirect('crear_proyecto')  # Redirige a la página de proyectos
    else:
        form = ProyectoForm()

    proyectos = Proyecto.objects.all()  # Obtén todos los proyectos
    return render(request, 'agua/crear_proyecto.html', {'form': form, 'proyectos': proyectos})

@user_passes_test(es_superusuario)
def editar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('proyecto_comunidad', proyecto_id=proyecto.id)
    else:
        form = ProyectoForm(instance=proyecto)

    return render(request, 'agua/editar_proyecto.html', {'form': form, 'proyecto': proyecto})

@user_passes_test(es_superusuario)
def eliminar_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    proyecto.delete()
    messages.success(request, 'Proyecto eliminado correctamente.')
    return redirect('crear_proyecto')

from django.http import HttpResponseServerError
import logging
logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: u.is_staff)
def proyecto_comunidad(request, proyecto_id):
    try:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        if not request.user.is_superuser:
            return redirect('proyectos_disponibles')

        ideas = proyecto.ideas.all().annotate(total_me_gusta=Count('me_gusta')).order_by('-total_me_gusta')
        idea_mas_gustada = ideas.first()

        return render(request, 'agua/proyecto_comunidad.html', {
            'proyecto': proyecto,
            'idea_mas_gustada': idea_mas_gustada,
            'ideas': ideas
        })

    except Exception as e:
        logger.error(f"Error en proyecto_comunidad: {str(e)}")
        return HttpResponseServerError("Error interno. Contacte al administrador.")
@login_required
@user_passes_test(lambda u: u.is_superuser)
def usuarios_registrados(request):
    usuarios = User.objects.filter(is_superuser=False).order_by('-date_joined')
    return render(request, 'agua/usuarios.html', {'usuarios': usuarios})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def mensajes(request):
    mensajes_no_responder = MensajeContacto.objects.filter(respuesta__isnull=True).order_by('-fecha')
    mensajes_respondidos = MensajeContacto.objects.filter(respuesta__isnull=False).order_by('-fecha')
    
    return render(request, 'agua/mensajes.html', {
        'mensajes_no_responder': mensajes_no_responder,
        'mensajes_respondidos': mensajes_respondidos
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def responder_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(MensajeContacto, id=mensaje_id)

    if request.method == 'POST':
        form = ResponderMensajeForm(request.POST)
        if form.is_valid():
            asunto = form.cleaned_data['asunto']
            cuerpo = form.cleaned_data['respuesta']
            
            # Enviar email usando EmailMessage para manejar correctamente la codificación
            email = EmailMessage(
                subject=asunto,
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[mensaje.email],
            )
            email.content_subtype = "plain"  # Si prefieres texto plano
            email.encoding = 'utf-8'  # Asegura que se maneje correctamente la codificación UTF-8
            email.send(fail_silently=False)

            # Marcar el mensaje como respondido
            mensaje.respuesta = cuerpo
            mensaje.respondido = True
            mensaje.save()

            # Redirigir al panel de administración
            return redirect('mensajes')
    else:
        form = ResponderMensajeForm()

    return render(request, 'agua/responder_mensaje.html', {
        'form': form,
        'mensaje': mensaje,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_mensaje(request, mensaje_id):
    mensaje = get_object_or_404(MensajeContacto, id=mensaje_id)
    mensaje.delete()
    return redirect('admin_panel')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def panel_ajustes(request):
    if request.method == 'POST':
        perfil_form = AdminUpdateForm(request.POST, instance=request.user)
        password_form = AdminCambiarContrasenaForm(request.user, request.POST)

        if 'actualizar_perfil' in request.POST and perfil_form.is_valid():
            perfil_form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('panel_ajustes')

        elif 'cambiar_contraseña' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Para que no cierre sesión
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('panel_ajustes')

        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        perfil_form = AdminUpdateForm(instance=request.user)
        password_form = AdminCambiarContrasenaForm(request.user)

    return render(request, 'agua/ajustes.html', {
        'perfil_form': perfil_form,
        'password_form': password_form
    })


#Iniciar sesión y cerrar sesión
def login_view(request):
    if request.user.is_authenticated:
        # Si el usuario ya está logueado, redirigir según el tipo
        if request.user.is_superuser:
            return redirect('admin_panel')
        else:
            return redirect('panel_usuario')

    error = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # usamos el alias
                if user.is_superuser:
                    return redirect('admin_panel')
                else:
                    return redirect('panel_usuario')
            else:
                error = 'Credenciales inválidas.'
    else:
        form = LoginForm()

    return render(request, 'agua/login.html', {'form': form, 'error': error})

def logout_view(request):
    auth_logout(request)
    return redirect('login')


#Index
def index(request):
    noticias = obtener_noticias_ods6()
    return render(request, 'agua/index.html', {'noticias': noticias})


#Estadísticas
def estadisticas(request):
    return render(request, 'agua/estadisticas.html')


#¿Qué es?
def que_es(request):
    return render(request, 'agua/que_es.html')


#Solución
def solucion(request):
    return render(request, 'agua/solucion.html')


#Ayudar
def ayudar(request):
    return render(request, 'agua/ayudar.html')


#Contacto
def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Gracias por tu mensaje! Te contactaremos pronto.")
            form = ContactoForm()
    else:
        form = ContactoForm()
    
    return render(request, 'agua/contacto.html', {'form': form})


#Usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')  # Puedes redirigir al login
    else:
        form = RegistroForm()
    return render(request, 'agua/registro.html', {'form': form})

@login_required
def panel_usuario(request):
    noticias = obtener_noticias_ods6()
    return render(request, 'agua/panel_usuario.html', {'noticias': noticias})

@login_required
def mis_mensajes(request):
    mensajes = MensajeContacto.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'agua/mis_mensajes.html', {'mensajes': mensajes})

@login_required
def contacto_usuario(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.usuario = request.user
            mensaje.save()
            messages.success(request, "¡Tu mensaje ha sido enviado correctamente!")
            form = ContactoForm()
    else:
        form = ContactoForm(initial={
            'nombre': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        })
    
    return render(request, 'agua/contacto_usuario.html', {'form': form})

@login_required
def ajustes_usuario(request):
    if request.method == 'POST':
        # Si se está enviando el formulario de actualización de datos
        if 'update_data' in request.POST:
            form = ActualizarUsuarioForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "¡Datos actualizados correctamente!")
                return redirect('ajustes_usuario')  # Redirige para mostrar los cambios
        
        # Si se está enviando el formulario de cambio de contraseña
        elif 'change_password' in request.POST:
            password_form = CambiarContrasenaForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, "¡Contraseña cambiada correctamente!")
                return redirect('ajustes_usuario')  # Redirige para mostrar el cambio

    else:
        form = ActualizarUsuarioForm(instance=request.user)  # Formulario para nombre y correo
        password_form = CambiarContrasenaForm(user=request.user)  # Formulario para cambiar contraseña

    return render(request, 'agua/ajustes_usuario.html', {
        'form': form,
        'password_form': password_form,
    })

@login_required
def proyectos_disponibles(request):
    proyectos = Proyecto.objects.all()
    proyectos_unidos = request.user.proyectos_unidos.all()
    return render(request, 'agua/proyectos_disponibles.html', {
        'proyectos': proyectos,
        'proyectos_unidos': proyectos_unidos,
    })

@login_required
def unirse_o_salir_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    # Si el usuario ya está en el proyecto, lo eliminamos
    if proyecto.miembros.filter(id=request.user.id).exists():
        proyecto.miembros.remove(request.user)
    else:
        proyecto.miembros.add(request.user)

    return redirect('proyectos_disponibles')

@login_required
def proyecto_comunidad_usuario(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        form = IdeaUsuarioForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.usuario = request.user
            idea.proyecto = proyecto
            idea.save()
            return redirect('proyecto_comunidad_usuario', proyecto_id=proyecto.id)
    else:
        form = IdeaUsuarioForm()

    ideas = IdeaUsuario.objects.filter(proyecto=proyecto).order_by('-fecha')

    # Obtener la idea más gustada
    idea_mas_gustada = IdeaUsuario.objects.filter(proyecto=proyecto).annotate(
        total_me_gusta=Count('me_gusta')
    ).order_by('-total_me_gusta').first()

    context = {
        'proyecto': proyecto,
        'form': form,
        'ideas': ideas,
        'idea_mas_gustada': idea_mas_gustada,  # Pasamos la idea más gustada al contexto
    }
    return render(request, 'agua/proyecto_comunidad_usuario.html', context)

@login_required
def editar_idea(request, proyecto_id, idea_id):
    idea = get_object_or_404(IdeaUsuario, id=idea_id, proyecto_id=proyecto_id)
    if idea.usuario != request.user:
        return HttpResponseForbidden("No tienes permiso para editar esta idea.")
    
    if request.method == 'POST':
        form = IdeaUsuarioForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            return redirect('proyecto_comunidad_usuario', proyecto_id=proyecto_id)
    else:
        form = IdeaUsuarioForm(instance=idea)

    return render(request, 'agua/editar_idea.html', {'form': form, 'proyecto_id': proyecto_id})

@login_required
def eliminar_idea(request, proyecto_id, idea_id):
    idea = get_object_or_404(IdeaUsuario, id=idea_id, proyecto_id=proyecto_id)
    
    # Verifica si el usuario es el propietario de la idea
    if idea.usuario != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar esta idea.")
    
    if request.method == 'POST':
        idea.delete()
        return redirect('proyecto_comunidad_usuario', proyecto_id=proyecto_id)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def marcar_me_gusta(request, proyecto_id, idea_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    idea = get_object_or_404(IdeaUsuario, id=idea_id)

    # Asegúrate de que el usuario esté autenticado
    if request.user.is_authenticated:
        if request.user not in idea.me_gusta.all():
            idea.me_gusta.add(request.user)
        else:
            idea.me_gusta.remove(request.user)

    return redirect('proyecto_comunidad_usuario', proyecto_id=proyecto.id)

