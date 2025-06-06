
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
