from os import environ

CONFIGS_MODULE_ATTR = 'uwsgi_configuration'

ENV_CONF_ALIAS = 'UWSGICONF_CONF_ALIAS'
ENV_CONF_READY = 'UWSGICONF_READY'
ENV_FORCE_STUB = 'UWSGICONF_FORCE_STUB'


FORCE_STUB = int(environ.get(ENV_FORCE_STUB, 0))
"""Forces using stub instead of uwsgi real module."""
