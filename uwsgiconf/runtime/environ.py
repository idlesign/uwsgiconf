from warnings import warn

from .platform import uwsgi as uwsgi_env

warn('runtime.environ.uwsgi_env is deprecated. Please use runtime.platform.uwsgi', DeprecationWarning)
