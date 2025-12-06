import inspect
from collections.abc import Callable, Iterable
from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING, Any, NamedTuple, Optional

if TYPE_CHECKING:
    from uwsgiconf.runtime.locking import Lock

from ..settings import ENV_SKIP_TASK, get_maintenance_inplace, get_skip_task


class SigHandlerAbilities(NamedTuple):
    pass_context: bool
    pass_args: bool


class TaskContext:
    """Object allowing task context pass to task functions."""

    def __init__(
            self,
            *,
            params: dict | None = None,
            last_result: dict | None = None,
            obj: Any = None
    ):
        """
        :param params: Task parameters.
        :param last_result: Task result from the last (previous) run.
        :param obj: Raw task object (if provided by a backend).
        """
        self.params = params or {}
        self.result = None
        self.last_result = last_result or {}
        self.obj = obj


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
    """Dummy task backend. Does nothing."""


class TaskChecker:
    """Facilitates task execution requirements checking."""

    def __init__(
            self,
            *,
            env: str | bool = True,
            maintenance: bool = True,
            lock: Optional['Lock'] = None,
            checkers: Iterable[Callable[[str], bool]] | None = None,
    ):
        """

        :param env: Environment variable name to check whether
            task execution should be skipped. E.g. for temporary maintenance.
            By default, with UWSGICONF_SKIP_TASK_{task}=1 tasks will be ignored.

        :param maintenance: Prevents background task execution in maintenance mode.
            Watches for UWSGICONF_MAINTENANCE=1 environment variable.

        :param lock: uWSGI lock to check before task run.
            If the lock is set, the task execution will be skipped.
            Can be useful for graceful shutdown on rollout in distributed environment,
            when new background tasks are marked not to run from a worker process (e.g. by an API request),
            and then the app is stopped itself.

        :param checkers: Custom checking functions. Require to accept task name argument and
            return True to skip task execution.

        """
        checkers_: list[Callable[[str], bool]] = [
            *(checkers or []),
        ]

        if maintenance:
            checkers_.append(lambda task_name: get_maintenance_inplace())

        if env:
            if isinstance(env, bool):
                env = ENV_SKIP_TASK
            checkers_.append(partial(get_skip_task, env_var=env))

        if lock:
            checkers_.append(lambda task_name: lock.is_set)

        checkers_.extend(checkers or [])

        self.checkers = checkers_

    def needs_skip(self, task_name: str) -> bool:
        for checker_func in self.checkers:
            if checker_func(task_name=task_name):
                return True
        return False


def taskfunc_inspect(func: Callable) -> SigHandlerAbilities:
    params = inspect.signature(func).parameters
    params_len = len(params)
    pass_context = 'ctx' in params

    pass_args = True
    if not params_len or (pass_context and params_len == 1):
        # do not try to pass uwsgi signal num into func
        pass_args = False

    return SigHandlerAbilities(pass_context=pass_context, pass_args=pass_args)


def taskfunc_get_args(
        *,
        abilities: SigHandlerAbilities,
        args: tuple,
        kwargs: dict,
        ctx: TaskContext | None = None
) -> tuple:
    if abilities.pass_context:
        kwargs['ctx'] = ctx

    if not abilities.pass_args:
        args = ()

    return args, kwargs
