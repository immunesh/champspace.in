from django.apps import AppConfig


class ChampappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'champapp'


# champapp/apps.py
from django.apps import AppConfig

class ChampappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'champapp'

    def ready(self):
        import champapp.signals  # Import the signals
