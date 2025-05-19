from django import forms
from .models import MensajeContacto
from .models import Proyecto
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm
from .models import IdeaUsuario


class AdminUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
        }
        help_texts = {
            'username': '',  # Oculta el texto "Required. 150 characters..."
            'email': '',     # Oculta cualquier texto de ayuda en email
        }

class AdminCambiarContrasenaForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(AdminCambiarContrasenaForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].label = "Nueva Contraseña"
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].help_text = ""

        self.fields['new_password2'].label = "Confirmar Nueva Contraseña"
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].help_text = ""

class RegistroForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar Contraseña"
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'username': '',
            'email': '',
        }
        error_messages = {
            'username': {
                'unique': 'Este nombre de usuario ya está en uso.',
                'required': 'Este campo es obligatorio.',
            },
            'email': {
                'required': 'Este campo es obligatorio.',
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=100)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
        }

    # Eliminar los textos de ayuda (help_text)
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre",
        help_text=""  # Esto elimina el texto de ayuda para el nombre
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Correo Electrónico",
        help_text=""  # Esto elimina el texto de ayuda para el correo electrónico
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label="Mensaje",
        help_text=""  # Esto elimina el texto de ayuda para el mensaje
    )

class ResponderMensajeForm(forms.Form):
    asunto = forms.CharField(max_length=100)
    respuesta = forms.CharField(widget=forms.Textarea, label='Mensaje de respuesta')
    
class ActualizarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Aquí agregamos solo los campos necesarios
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    # Eliminar o personalizar los textos de ayuda (help_text)
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Nombre de Usuario",
        help_text=""  # Esto elimina el texto de ayuda para el nombre de usuario
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Correo Electrónico",
        help_text=""  # Esto elimina el texto de ayuda para el correo electrónico
    )

class CambiarContrasenaForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
        widgets = {
            'old_password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'new_password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'new_password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    # Eliminar o personalizar los textos de ayuda de las contraseñas
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña Actual"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nueva Contraseña",
        help_text=""  # Esto elimina el texto de ayuda para la nueva contraseña
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar Nueva Contraseña",
        help_text=""  # Esto elimina el texto de ayuda para confirmar la nueva contraseña
    )
    
    
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'idea_principal']
        
        
class IdeaUsuarioForm(forms.ModelForm):
    class Meta:
        model = IdeaUsuario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Comparte tu idea...'})
        }