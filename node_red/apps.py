from django.apps import AppConfig

class NodeRedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node_red'
    def ready(self):
        import node_red.signals