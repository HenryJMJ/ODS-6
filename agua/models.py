from django.db import models
from django.contrib.auth.models import User

class MensajeContacto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    respondido = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.email})"

class UsuarioLeido(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Leído: {self.user.username} - {self.leido}"
    
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    idea_principal = models.TextField(blank=True, null=True) 
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proyectos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    miembros = models.ManyToManyField(User, related_name='proyectos_unidos', blank=True)

    def __str__(self):
        return self.nombre
    
class IdeaUsuario(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='ideas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    me_gusta = models.ManyToManyField(User, related_name='me_gusta_ideas', blank=True)  # Relación de 'me gusta'

    @property
    def me_gusta_count(self):
        return self.me_gusta.count()