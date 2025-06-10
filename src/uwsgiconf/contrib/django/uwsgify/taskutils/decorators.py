import inspect
from functools import wraps
from os import environ
from time import sleep

from ..settings import SKIP_TASK_ENV_VAR
from .backends import BackendBase


def task(
        cooldown: int = 0,
        env_var_skip: str = SKIP_TASK_ENV_VAR,
        backend: BackendBase | None = None,
):
    """Decorator useful for task functions (e.g. uWSGI cron, timer).

    :param cooldown: Number of seconds to sleep after function execution.
        Useful if uWSGI in different datacenters are desynchronized.

    :param env_var_skip: Environment variable name to check whether
        task execution should be skipped. E.g. for temporary maintenance.
        By default, with UWSGIFY_SKIP_TASK=1 tasks will be ignored.

    :param backend: Distributed task backend.
        Consecutive calls of the decorated task function, when it is blocked (already running),
        will be ignored (the decorated function will return None).

        Can be useful to run scheduled functions exclusively in one datacenter
        (implies a distributed cache, such as Redis or Database).

        If not set, BackendBase is used.
        See .backends module for available backends.

    """
    backend = backend or BackendBase()

    def task_(func):

        params = inspect.signature(func).parameters
        params_len = len(params)
        pass_context = 'ctx' in params

        pass_args = True
        if not params_len or (pass_context and params_len == 1):
            # do not try to pass uwsgi signal num into func
            pass_args = False

        @wraps(func)
        def wrapper(*args, **kwargs):
            if environ.get(env_var_skip) == '1':
                return

            with backend(func) as ctx:
                if ctx:
                    if pass_context:
                        kwargs['ctx'] = ctx

                    if not pass_args:
                        args = ()

                    result = func(*args, **kwargs)

                else:
                    result = None

            cooldown and sleep(cooldown)

            return result

        return wrapper

    return task_
