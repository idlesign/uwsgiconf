# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django import db
from django.apps import apps
from django.utils.module_loading import autodiscover_modules

from uwsgiconf import uwsgi
from uwsgiconf.exceptions import RuntimeConfigurationError
from .settings import MODULE_INIT


def check_for_stub():
    """Check for uWSGI stub. Disallow it to prevent
    stub module caching when embedded mode with pyuwsgi is used."""

    if not uwsgi.is_stub:
        return

    msg = (
        'Something from uwsgiconf.uwsgi has been imported before uWSGI start. '
        'Please move uWSGI related stuff including such imports '
        'into %s.py modules of your apps.' % MODULE_INIT)

    raise RuntimeConfigurationError(msg)


check_for_stub()


from uwsgiconf.runtime.platform import uwsgi


@uwsgi.postfork_hooks.add()
def db_close_connections():
    """Close db connections after fork()."""
    db.connections.close_all()


if apps.apps_ready:
    # Only for embedded mode. For non-embedded see UwsgifyConfig.ready()
    # Import uWSGI init modules from applications.
    autodiscover_modules(MODULE_INIT)
