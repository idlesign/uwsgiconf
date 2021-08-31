import os

import pytest


@pytest.fixture
def patch_project_dir(monkeypatch):
    monkeypatch.setattr('uwsgiconf.contrib.django.uwsgify.toolbox.find_project_dir', lambda: 'dummy')


@pytest.fixture
def patch_base_command(monkeypatch, patch_project_dir, tmpdir):

    fifofile = tmpdir.join('some.fifo')
    fifofile.write('')

    monkeypatch.setattr(
        'uwsgiconf.contrib.django.uwsgify.toolbox.SectionMutator.get_fifo_filepath',
        lambda project_name: f'{fifofile}')


def test_mutate_existing_section(patch_base_command):
    from uwsgiconf.contrib.django.uwsgify.toolbox import SectionMutator

    mutator = SectionMutator.spawn(dir_base=os.path.dirname(__file__))
    assert mutator.section.name == 'testdummy'


def test_uwsgi_run(monkeypatch, patch_project_dir, command_run, settings, tmpdir, capsys):

    def runtime_dir(self):
        return f'{tmpdir}'

    monkeypatch.setattr('os.execvp', lambda *args, **kwargs: None)
    monkeypatch.setattr('uwsgiconf.contrib.django.uwsgify.toolbox.SectionMutator.runtime_dir', property(runtime_dir))

    with settings(STATIC_ROOT=f'{tmpdir}'):
        command_run('uwsgi_run')

    out, err = capsys.readouterr()
    assert tmpdir.join('admin').exists()
    assert tmpdir.join('uwsgify').exists()
    assert 'static files copied' in out

    command_run('uwsgi_run', options={'compile': True})
    out, err = capsys.readouterr()
    assert 'error-page-404 = replaceit/uwsgify/404.html' in out

    with pytest.raises(ImportError) as e:  # py3 - ModuleNotFoundError
        command_run('uwsgi_run', options={'embedded': True})
    out, err = capsys.readouterr()
    assert 'Deleting' in out
    assert f'{e.value}' == "No module named 'pyuwsgi'"


def test_uwsgi_log(patch_base_command, command_run):
    command_run('uwsgi_log', options={'reopen': True})


def test_uwsgi_reload(patch_base_command, command_run):
    command_run('uwsgi_reload')


def test_uwsgi_stats(patch_base_command, command_run):
    command_run('uwsgi_stats')


def test_uwsgi_stop(patch_base_command, command_run):
    command_run('uwsgi_stop')


def test_uwsgi_sysinit_systemd(patch_base_command, capsys, command_run):
    command_run('uwsgi_sysinit', options={'systype': 'systemd', 'nostatic': True, 'noruntimes': True})

    out, err = capsys.readouterr()

    uid = os.getuid()

    assert not err
    assert ('-o %s -g %s' % (uid, os.getgid())) in out
    assert ('/run/user/%s/dummy' % uid) in out
    assert 'Description=dummy uWSGI Service' in out
    assert 'bin/python' in out
    assert 'dummy/manage.py uwsgi_run --nostatic --noruntimes\n' in out


def test_uwsgi_sysinit_upstart(patch_base_command, capsys, command_run):
    command_run('uwsgi_sysinit', options={'systype': 'upstart', 'nostatic': True})

    out, err = capsys.readouterr()

    assert not err
    assert 'description "dummy uWSGI Service"' in out
    assert 'bin/python' in out
    assert 'dummy/manage.py uwsgi_run' in out


class TestAdmin:

    def test_configuration(self, request_client, user_create):

        client = request_client(user=user_create(superuser=True))
        data = client.get('/admin/uwsgify/configuration/').content.decode()
        assert 'This site is not served by uWSGI.' in data

    def test_summary(self, request_client, user_create):
        from uwsgiconf.runtime.signals import Signal

        signal = Signal()

        @signal.register_handler()
        def somefunc():
            pass

        client = request_client(user=user_create(superuser=True))
        data = client.get('/admin/uwsgify/summary/').content.decode()
        assert 'Requests total' in data
        assert '0 - worker: test_django.somefunc' in data

    def test_workers(self, request_client, user_create):

        client = request_client(user=user_create(superuser=True))
        data = client.get('/admin/uwsgify/workers/').content.decode()
        assert 'This site is not served by uWSGI.' in data

    def test_maintenance(self, request_client, user_create, monkeypatch, tmpdir):

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

        monkeypatch.setattr('uwsgiconf.settings.get_maintenance_path', lambda: f'/')
        data = client.post('/admin/uwsgify/maintenance/', data={'confirm': 'maintenance'}).content.decode()
        assert 'Unable to schedule' in data
