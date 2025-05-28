from django.conf import settings

MODULE_INIT_DEFAULT = 'uwsgiinit'
"""Default name for uwsgify init modules."""


MODULE_INIT = getattr(settings, 'UWSGIFY_MODULE_INIT', MODULE_INIT_DEFAULT)
"""Name of a module with uWSGI runtime related stuff 
to automatically import from registered applications.

"""

SKIP_TASK_ENV_VAR = getattr(settings, 'UWSGIFY_SKIP_TASK_ENV_VAR', 'UWSGIFY_SKIP_TASK')
"""Environment variable name to check whether
task execution should be skipped. E.g. for temporary maintenance.
See `task` and `task_locked` decorators.

"""
