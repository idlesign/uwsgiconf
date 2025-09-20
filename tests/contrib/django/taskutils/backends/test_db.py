from unittest.mock import patch

import pytest

from uwsgiconf.contrib.django.uwsgify.models import Task
from uwsgiconf.contrib.django.uwsgify.taskutils.backends import DbBackend
from uwsgiconf.contrib.django.uwsgify.taskutils.context import TaskContext
from uwsgiconf.contrib.django.uwsgify.taskutils.decorators import task
from uwsgiconf.runtime.scheduling import register_timer


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

    # deactivate
    task_obj.active = False
    task_obj.save()
    task_1 = task(backend=backend)(mytask)
    assert task_1() is None


@patch('uwsgiconf.contrib.django.uwsgify.taskutils.decorators.sleep')
def test_db_exception(sleep):

    @register_timer(10)
    @task(cooldown=10, backend=DbBackend())
    def task_with_exc():
        raise ValueError('dammed')

    task_obj = Task.register('task_with_exc')

    with pytest.raises(ValueError, match='dammed'):
        task_with_exc()

    task_obj.refresh_from_db()
    assert task_obj.released

    assert sleep.called


@patch('uwsgiconf.contrib.django.uwsgify.taskutils.decorators.sleep')
def test_db_sleep(sleep):

    @register_timer(10)
    @task(cooldown=10, backend=DbBackend())
    def task_no_exc():
        return 'done'

    task_obj = Task.register('task_no_exc')

    assert task_no_exc() == 'done'

    task_obj.refresh_from_db()
    assert task_obj.released

    assert sleep.called


def test_admin_run_task(request_client, user_create):
    @register_timer(10)
    @task(backend=DbBackend())
    def task_to_force(*, ctx):
        ctx.result = {'q': 'w'}
        return 'some'

    client = request_client(user=user_create(superuser=True))
    task_obj = Task.register('task_to_force')
    task_missing = Task.register('task_unknown')

    data = client.post(
        '/admin/uwsgify/task/',
        data={
            'action': 'run_now',
            '_selected_action': [f'{task_obj.id}', f'{task_missing.id}'],
        },
        follow=True
    ).content.decode()

    assert 'Running: task_to_force' in data
    assert 'Unable to run tasks unregistered with uWSGI: task_unknown' in data
