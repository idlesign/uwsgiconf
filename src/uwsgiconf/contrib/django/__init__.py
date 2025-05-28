import sys
from pathlib import Path

# To support 'uwsgiconf.contrib.django.uwsgify' in INSTALLED_APPS:
sys.path.insert(0, Path(__file__).parent)
