import os
import sys

import django

BASE_DIR = os.path.dirname(os.getcwd())
sys.path.extend([BASE_DIR])
os.environ['DJANGO_SETTINGS_MODULE'] = 'entrance.settings'

if 'setup' in dir(django):
    django.setup()
