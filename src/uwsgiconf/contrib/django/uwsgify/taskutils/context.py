import warnings

from uwsgiconf.runtime.task_utils import TaskContext  # noqa

warnings.warn("Please import from runtime.task_utils", DeprecationWarning, stacklevel=2)
