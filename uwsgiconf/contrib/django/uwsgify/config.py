from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UwsgifyConfig(AppConfig):

    name = 'uwsgify'
    verbose_name = _('uWSGI Integration')
