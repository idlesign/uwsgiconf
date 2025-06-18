from collections.abc import Callable
from contextlib import contextmanager
from socket import gethostname

from django.core.cache import caches
from django.utils import timezone

from ..models import Task
from .context import TaskContext
from .models import TaskBase


class BackendBase:

    def __init__(self, *, strict: bool = True, context: type[TaskContext] | None = None):
        """
        :param strict: If False, exceptions related to task acquirement
            are silenced, effectively allowing task run without a lock.

        :param context: Task context class. If not set, default TaskContext is used.

        """
        self._strict = strict
        self._ctx = context or TaskContext

    @contextmanager
    def __call__(self, func: Callable):
        name = self._get_name(func)
        ctx = None

        try:
            ctx = self._acquire(name)

        except Exception as e:  # noqa: BLE001
            self._handle_exception(e, name=name)

        finally:
            try:
                yield ctx

            except Exception as e:  # noqa: BLE001
                self._handle_exception(e, name=name)

            finally:
                if ctx:
                    self._release(name=name, ctx=ctx)

    def _get_name(self, func: Callable) -> str:
        return func.__name__

    def _acquire(self, name: str) -> TaskContext | None:
        return self._ctx()

    def _handle_exception(self, exc: Exception, *, name: str) -> bool:
        if not self._strict:
            return False

        raise exc

    def _release(self, *, name: str, ctx: TaskContext):
        pass


class DummyBackend(BackendBase):
    """Dummy distributed backend. Does nothing."""


class CacheBackend(BackendBase):
    """Allows locking the execution of task function (e.g. uWSGI cron, timer)
    with the help of Django cache.
    """

    def __init__(self, *, cache_name: str, strict: bool = True, timeout: int = 1200):
        """

        :param cache_name: Django cache alias.

        :param strict: If False, locking exceptions are silenced,
            effectively allowing task run without a lock.

        :param timeout: Cache entry timeout (seconds).

        """
        super().__init__(strict=strict)
        self._cache_name = cache_name
        self._timeout = timeout

    def _get_name(self, func: Callable) -> str:
        return f'lock_{super()._get_name(func)}'

    def _acquire(self, name: str) -> TaskContext | None:
        caches[self._cache_name].add(
            name,
            value=f"{gethostname()}@{timezone.now()}",
            timeout=self._timeout
        )
        return super()._acquire(name)

    def _release(self, *, name: str, ctx: TaskContext):
        caches[self._cache_name].delete(name)


class DbBackend(BackendBase):
    """Allows locking the execution of task function (e.g. uWSGI cron, timer)
    with the help of Django DB, using custom task parameters and storing run result."""

    def __init__(self, *, model_cls: TaskBase | None = None, strict: bool = True):
        """
        :param model_cls: Django model class.

        :param strict: If False, locking exceptions are silenced,
            effectively allowing task run without a lock.

        """
        super().__init__(strict=strict)
        self._model_cls = model_cls or Task

    def _acquire(self, name: str) -> TaskContext | None:
        task_obj = self._model_cls.acquire(name)

        if not task_obj:
            return None

        return self._ctx(
            params=task_obj.params,
            last_result=task_obj.result,
            obj=task_obj
        )

    def _release(self, *, name: str, ctx: TaskContext):
        ctx.obj.release(result=ctx.result)
