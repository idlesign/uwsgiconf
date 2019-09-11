from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UwsgifyConfig(AppConfig):

    name = 'uwsgiconf.contrib.django.uwsgify'
    verbose_name = _('uWSGI Integration')
