from django.apps import AppConfig

class AguaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agua'

    def ready(self):
        import agua.signals  # Asegúrate de que las señales se registren correctamente