import pytest


@pytest.fixture
def patch_project_dir(monkeypatch):
    monkeypatch.setattr('uwsgiconf.contrib.django.uwsgify.toolbox.find_project_dir', lambda: 'dummy')


@pytest.fixture
def patch_base_command(monkeypatch, patch_project_dir, tmpdir):

    class Command(object):
        pass

    class Error(Exception):
        pass

    monkeypatch.setattr('django.core.management.base.BaseCommand', Command)
    monkeypatch.setattr('django.core.management.base.CommandError', Error)
    monkeypatch.setattr('django.core.management.base.CommandError', Error)

    fifofile = tmpdir.join('some.fifo')
    fifofile.write('')

    monkeypatch.setattr(
        'uwsgiconf.contrib.django.uwsgify.toolbox.SectionMutator.get_fifo_filepath',
        lambda project_name: fifofile)


def test_uwsgi_run(monkeypatch, patch_project_dir):

    def exec(cmd, args):
        pass

    class Settings(object):

        MEDIA_URL = '/static/media/'
        MEDIA_ROOT = '/dummy/media/'
        STATIC_URL = '/static/'
        STATIC_ROOT = '/dummy/static/'

    def call_command(*args, **kwargs):
        return

    monkeypatch.setattr('django.core.management.call_command', call_command)
    monkeypatch.setattr('django.conf.settings', Settings)
    monkeypatch.setattr('os.execvp', exec)

    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_run import Command

    Command().handle(compile=False, use_static_handler=True)


def test_uwsgi_log(patch_base_command):
    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_log import Command

    Command().handle(reopen=True, rotate=False)


def test_uwsgi_reload(patch_base_command):
    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_reload import Command

    Command().handle(force=False, workers=False, chain=False)


def test_uwsgi_stats(patch_base_command):
    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_stats import Command

    Command().handle()


def test_uwsgi_stop(patch_base_command):
    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_stop import Command

    Command().handle(force=False)
