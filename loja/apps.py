from django.apps import AppConfig


class LojaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'loja'
    verbose_name = 'Sistema de Vendas'

    def ready(self):
        """
        Import signals when app is ready
        """
        import loja.signals
