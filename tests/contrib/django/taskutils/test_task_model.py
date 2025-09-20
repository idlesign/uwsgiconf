from freezegun import freeze_time

from tests.testapp.models import Task


def test_basic():
    assert Task.acquire("some") is None

    task_other_name = 'other'

    # register
    task = Task.register(task_other_name, params={"a": "b"})
    assert f'{task}' == task_other_name
    assert task.dt_created
    dt_updated = task.dt_updated
    assert dt_updated
    assert task.dt_acquired is None
    assert task.dt_released is None
    assert not task.owner
    assert task.released
    assert task.params == {"a": "b"}
    assert task.result == {}

    # acquire just registered
    task = Task.acquire(task_other_name)
    assert task == task
    assert task.dt_updated != dt_updated
    assert task.dt_acquired
    assert task.dt_released is None
    assert task.owner
    assert not task.released
    assert task.params == {"a": "b"}
    assert task.result == {}

    # unable to reacquire
    assert Task.acquire(task_other_name) is None

    # release
    task.release(result={"d": "f"})
    task.refresh_from_db()
    assert task == task
    assert task.dt_acquired
    assert task.dt_released
    assert task.owner
    assert task.released
    assert task.params == {"a": "b"}
    assert task.result == {"d": "f"}

    # able to reacquire
    assert Task.acquire(task_other_name)


def test_acquire_active():
    task = Task.register('one', active=False)
    assert Task.acquire('one') is None
    assert Task.acquire('one', active=False) == task


def test_reset_stale():
    with freeze_time('2025-02-05 15:00:00'):
        task = Task.register("stale", released=False)

    assert not task.released

    Task.reset_stale()
    task.refresh_from_db()
    assert task.released
