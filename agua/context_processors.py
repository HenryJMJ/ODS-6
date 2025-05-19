from .models import MensajeContacto, UsuarioLeido

def notificaciones_context(request):
    # Contar mensajes no respondidos
    mensajes_no_respondidos = MensajeContacto.objects.filter(respondido=False).count()
    
    # Contar usuarios no leídos
    usuarios_no_leidos = UsuarioLeido.objects.filter(leido=False).count()
    
    return {
        'usuarios_no_leidos': usuarios_no_leidos,
        'mensajes_no_respondidos': mensajes_no_respondidos
    }
