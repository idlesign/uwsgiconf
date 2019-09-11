from __future__ import absolute_import

from sys import modules
from os import environ as __env

from .settings import ENV_FORCE_STUB
from .exceptions import UwsgiconfException as __DummyException


if False:  # pragma: nocover
    # Give IDEs a chance to load stub symbols.
    from .uwsgi_stub import *


try:  # pragma: nocover
    if __env.get(ENV_FORCE_STUB, False):
        raise __DummyException('`UWSGI_FORCE_STUB` is found in env.')

    import uwsgi

    uwsgi.is_stub = False  # type: bool
    """Indicates whether stub is used instead of real `uwsgi` module."""

    # The following allows proper dynamic attributes (e.g. ``env``) addressing.
    modules[__name__] = uwsgi

except (ImportError, __DummyException):

    from . import uwsgi_stub

    uwsgi_stub.is_stub = True  # type: bool
    """Indicates whether stub is used instead of real `uwsgi` module."""

    modules[__name__] = uwsgi_stub
