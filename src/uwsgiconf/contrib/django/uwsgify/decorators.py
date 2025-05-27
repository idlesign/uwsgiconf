from _socket import gethostname
from functools import wraps
from os import environ
from time import sleep

from django.core.cache import caches
from django.utils import timezone

from .settings import SKIP_TASK_ENV_VAR


def task(
        cooldown: int = 0,
        env_var_skip: str = SKIP_TASK_ENV_VAR,
):
    """Decorator useful for task functions (e.g. uWSGI cron, timer).

    :param cooldown: Number of seconds to sleep after function execution.
        Useful if uWSGI in different datacenters are desynchronized.

    :param env_var_skip: Environment variable name to check whether
        task execution should be skipped. E.g. for temporary maintenance.

    """
    def task_(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if environ.get(env_var_skip) == '1':
                return

            result = func(*args, **kwargs)
            cooldown and sleep(cooldown)

            return result

        return wrapper

    return task_


def task_locked(
        cache_name: str,
        *,
        timeout: int = 1200,
        strict: bool = True,
        cooldown: int = 4,
        env_var_skip: str = SKIP_TASK_ENV_VAR,
):
    """Decorator to lock the execution of task function (e.g. uWSGI cron, timer)
    with the help of Django cache.

    Consecutive calls of the decorated function, when it is blocked, will be ignored
    (the decorator will return None).

    Can be useful to run scheduled functions exclusively in one datacenter
    (implies a distributed cache, such as Redis or Database).

    :param cache_name: Django cache alias.

    :param timeout: Cache entry timeout (seconds).

    :param strict: If False, cache exceptions are silenced,
        effectively allowing task run without a lock.

    :param cooldown: Number of seconds to sleep after function execution.
        Useful if uWSGI in different datacenters are desynchronized.

    :param env_var_skip: Environment variable name to check whether
        task execution should be skipped. E.g. for temporary maintenance.

    """
    def task_locked_(func):
        lock_name = f"lock_{func.__qualname__}"
        hostname = gethostname()

        @task(cooldown=cooldown, env_var_skip=env_var_skip)
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = caches[cache_name]

            try:
                locked = cache.add(
                    lock_name,
                    value=f"{hostname}@{timezone.now()}",
                    timeout=timeout
                )
                cache_ok = True

            except Exception:
                if strict:
                    raise
                cache_ok = False
                locked = True

            if not locked:
                return

            try:
                result = func(*args, **kwargs)

            finally:
                if cache_ok:
                    cache.delete(lock_name)

            return result

        return wrapper

    return task_locked_
