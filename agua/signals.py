from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UsuarioLeido

@receiver(post_save, sender=User)
def crear_usuario_leido(sender, instance, created, **kwargs):
    if created:
        # Aquí añadimos un print para depuración
        print(f"Nuevo usuario creado: {instance.username} ({instance.email})")

        # Crear un objeto de UsuarioLeido para el nuevo usuario
        usuario_leido = UsuarioLeido.objects.create(user=instance)
        print(f"Objeto UsuarioLeido creado para: {instance.username}")

        # Verificar si la relación se creó correctamente
        if usuario_leido:
            print(f"UsuarioLeido creado correctamente para {instance.username}. Leído: {usuario_leido.leido}")
        else:
            print(f"Error al crear UsuarioLeido para {instance.username}")
