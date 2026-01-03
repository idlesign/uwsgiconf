from datetime import timedelta

from django.utils import timezone

from uwsgiconf.contrib.django.uwsgify.models import Task
from uwsgiconf.runtime.mules import Farm
from uwsgiconf.runtime.scheduling import register_cron


def test_configuration(request_client, user_create):

    client = request_client(user=user_create(superuser=True))
    data = client.get('/admin/uwsgify/configuration/').content.decode()
    assert 'This site is not served by uWSGI.' in data


def test_summary(request_client, user_create):
    from uwsgiconf.runtime.signals import Signal

    signal = Signal()

    @signal.register_handler()
    def somefunc():
        pass

    client = request_client(user=user_create(superuser=True))
    data = client.get('/admin/uwsgify/summary/').content.decode()
    assert 'Requests total' in data
    assert '0 - worker: tests.contrib.django.test_admin.somefunc' in data


def test_task(admin_client, user_create):

    farm = Farm('farm1')

    @register_cron(weekday=4, target=farm)
    def task_1():
        """My shiny task."""
        print("task_1")

    now = timezone.now()
    task_1_obj = Task.register("task_1", dt_acquired=now-timedelta(hours=2), dt_released=now-timedelta(minutes=35))
    task_2_obj = Task.register("task_2", dt_acquired=now-timedelta(hours=1), dt_released=now-timedelta(hours=8))

    admin_client.configure(app='uwsgify', model=Task)

    # Listing
    response = admin_client.call_listing()
    data = response.text
    assert '2 Task' in data
    assert '>task_1<' in data
    assert '>1:25:00<' in data  # duration
    assert '>task_2<' in data
    assert '>1:00:00<' in data  # duration

    # Details
    response = admin_client.call_change(task_1_obj)
    data = response.text
    assert '.task_1' in data
    assert 'My shiny task.' in data
    assert '<b>Target:</b> farm_farm1' in data
    assert 'weekday&#x27;: 4' in data

    # Details unknown task
    response = admin_client.call_change(task_2_obj)
    data = response.text
    assert 'is not registered within' in data


def test_workers(request_client, user_create):

    client = request_client(user=user_create(superuser=True))
    data = client.get('/admin/uwsgify/workers/').content.decode()
    assert 'This site is not served by uWSGI.' in data


def test_maintenance(request_client, user_create, monkeypatch, tmpdir):

    client = request_client(user=user_create(superuser=True))
    data = client.get('/admin/uwsgify/maintenance/').content.decode()
    assert 'This site is not served by uWSGI.' in data
    assert 'Maintenance mode is not supported' in data

    filepath = tmpdir.join('maintain')
    monkeypatch.setattr('uwsgiconf.settings.get_maintenance_path', lambda: f'{filepath}')

    data = client.get('/admin/uwsgify/maintenance/').content.decode()
    assert 'Remember: maintenance mode can only be' in data
    assert 'type="submit"' in data

    data = client.post('/admin/uwsgify/maintenance/', data={'confirm': 'bogus'}).content.decode()
    assert 'You need to enter' in data

    data = client.post('/admin/uwsgify/maintenance/', data={'confirm': 'maintenance'}).content.decode()
    assert 'Maintenance mode is scheduled' in data

    monkeypatch.setattr('uwsgiconf.settings.get_maintenance_path', lambda: '/')
    data = client.post('/admin/uwsgify/maintenance/', data={'confirm': 'maintenance'}).content.decode()
    assert 'Unable to schedule' in data
