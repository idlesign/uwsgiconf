from __future__ import absolute_import

from os import environ as __env
from sys import modules as __modules

from .exceptions import UwsgiconfException as __DummyException
from .settings import ENV_FORCE_STUB as __ENV_FORCE_STUB

if False:  # pragma: nocover
    # Give IDEs a chance to load stub symbols.
    from .uwsgi_stub import *


try:  # pragma: nocover
    if __env.get(__ENV_FORCE_STUB, False):
        raise __DummyException('`UWSGI_FORCE_STUB` is found in env.')

    import uwsgi

    uwsgi.is_stub = False  # type: bool
    """Indicates whether stub is used instead of real `uwsgi` module."""

    # The following allows proper dynamic attributes (e.g. ``env``) addressing.
    __modules[__name__] = uwsgi

except (ImportError, __DummyException):

    from . import uwsgi_stub
    __modules[__name__] = uwsgi_stub
