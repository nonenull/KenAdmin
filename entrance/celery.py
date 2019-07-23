# coding=utf-8
import os
from celery import Celery, platforms
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entrance .settings')

app = Celery('entrance ')
platforms.C_FORCE_ROOT = True

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])