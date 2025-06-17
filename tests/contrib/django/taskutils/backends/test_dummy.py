from typing import Any

from uwsgiconf.contrib.django.uwsgify.taskutils.backends import BackendBase
from uwsgiconf.contrib.django.uwsgify.taskutils.context import TaskContext
from uwsgiconf.contrib.django.uwsgify.taskutils.decorators import task
from uwsgiconf.runtime.locking import Lock
from uwsgiconf.runtime.scheduling import register_cron


def mytask_ctx(*, ctx: TaskContext):
    return f'{ctx.params}'


def test_basic():
    @register_cron()
    @task()
    def task_1():
        return 'some'

    assert task_1() == 'some'


class MyContext(TaskContext):

    def __init__(self, *, params: dict | None = None, last_result: dict | None = None, obj: Any = None):
        super().__init__(params=params, last_result=last_result, obj=obj)
        self.params["1"] = 2


def test_with_ctx():
    task_1 = task(backend=BackendBase(context=MyContext))(mytask_ctx)
    assert task_1() == "{'1': 2}"


def test_locked():
    lock = Lock(1)

    @register_cron()
    @task(lock_skip=lock)
    def task_1():
        return 'done'

    assert task_1() == "done"

    lock.acquire()
    assert task_1() is None

    lock.release()
    assert task_1() == "done"
