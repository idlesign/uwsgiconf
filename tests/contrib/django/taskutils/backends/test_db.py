from uwsgiconf.contrib.django.uwsgify.models import Task
from uwsgiconf.contrib.django.uwsgify.taskutils.backends import DbBackend
from uwsgiconf.contrib.django.uwsgify.taskutils.context import TaskContext
from uwsgiconf.contrib.django.uwsgify.taskutils.decorators import task


def mytask(*, ctx: TaskContext):
    ctx.result = {'d': 'f'}
    return f'{ctx.params}-{ctx.last_result}'


def test_db():
    backend = DbBackend()

    # unregistered task
    task_1 = task(backend=backend)(mytask)
    assert task_1() is None

    # registered task
    task_obj = Task.register('mytask', params={'a': 'b'}, result={'r': 't'})

    task_1 = task(backend=backend)(mytask)
    assert task_1() == "{'a': 'b'}-{'r': 't'}"  # last result is passed

    task_obj.refresh_from_db()
    assert task_obj.released
    assert task_obj.dt_acquired
    assert task_obj.dt_released
    assert task_obj.result == {'d': 'f'}  # new result is stored
