from django.contrib import admin
from .models import MensajeContacto
from .models import UsuarioLeido

admin.site.register(MensajeContacto)
admin.site.register(UsuarioLeido)