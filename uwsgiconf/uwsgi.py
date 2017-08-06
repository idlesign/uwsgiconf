from __future__ import absolute_import


try:
    is_stub = False  # type: bool
    """Indicates whether stub is used instead of real `uwsgi` module."""

    ####################################################################

    from uwsgi import *

except ImportError:

    is_stub = True  # type: bool
    """Indicates whether stub is used instead of real `uwsgi` module."""

    ####################################################################

    from .uwsgi_stub import *
