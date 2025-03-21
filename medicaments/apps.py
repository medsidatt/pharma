# medicaments/apps.py
from django.apps import AppConfig

class MedicamentsConfig(AppConfig):
    name = 'medicaments'

    def ready(self):
        import medicaments.signals  # Import the signals