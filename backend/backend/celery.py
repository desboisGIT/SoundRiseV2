import os
from celery import Celery

# Définir les paramètres Django pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Charger la configuration depuis settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discovery des tâches dans l'application Django
app.autodiscover_tasks()
