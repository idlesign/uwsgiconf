from os import environ

CONFIGS_MODULE_ATTR = 'uwsgi_configuration'

ENV_CONF_ALIAS = 'UWSGICONF_CONF_ALIAS'
ENV_CONF_READY = 'UWSGICONF_READY'
ENV_FORCE_STUB = 'UWSGICONF_FORCE_STUB'
ENV_MAINTENANCE = 'UWSGICONF_MAINTENANCE'
ENV_SKIP_TASK = 'UWSGICONF_SKIP_TASK_{task_name}'
ENV_MAINTENANCE_INPLACE = 'UWSGICONF_MAINTENANCE_INPLACE'


FORCE_STUB = int(environ.get(ENV_FORCE_STUB, 0))
"""Forces using stub instead of a real uwsgi module."""


def get_maintenance_path() -> str:
    """Return the maintenance trigger filepath.
    Introduced as a function to support embedded mode.

    """
    return environ.get(ENV_MAINTENANCE) or ''


def get_maintenance_inplace() -> bool:
    """Return the maintenance flag if it is set.
    Introduced as a function to support embedded mode.

    """
    return environ.get(ENV_MAINTENANCE_INPLACE, "0") != "0"


def get_skip_task(task_name: str, *, env_var: str = ENV_SKIP_TASK) -> bool:
    """Returns a flag from env indicating whether a task should be skipped.

    :param task_name: Task name.
    :param env_var: Environment variable to check.
        Note: if contains `{task_name}` placeholder, then it'll be replaced with the value from `name`.
    """
    return environ.get(env_var.format(task_name=task_name.upper()), "0") != "0"
