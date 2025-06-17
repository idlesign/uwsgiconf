import sys
from pathlib import Path

# To support 'uwsgiconf.contrib.django.uwsgify' in INSTALLED_APPS (old Python):
sys.path.insert(0, f'{Path(__file__).parent}')
