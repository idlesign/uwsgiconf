from __future__ import absolute_import

from os import environ as __env

from .settings import ENV_FORCE_STUB
from .exceptions import UwsgiconfException as __DummyException


try:  # pragma: nocover
    if __env.get(ENV_FORCE_STUB, False):
        raise __DummyException('`UWSGI_FORCE_STUB` is found in env.')

    is_stub = False  # type: bool
    """Indicates whether stub is used instead of real `uwsgi` module."""

    ####################################################################

    from uwsgi import *

except (ImportError, __DummyException):

    is_stub = True  # type: bool
    """Indicates whether stub is used instead of real `uwsgi` module."""

    ####################################################################

    from .uwsgi_stub import *
