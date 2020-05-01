import os
from sys import version_info

import pytest


@pytest.fixture
def patch_project_dir(monkeypatch):
    monkeypatch.setattr('uwsgiconf.contrib.django.uwsgify.toolbox.find_project_dir', lambda: 'dummy')


@pytest.fixture
def patch_base_command(monkeypatch, patch_project_dir, tmpdir, stub):

    class Settings(object):

        configured = True
        DEBUG = False
        STATIC_ROOT = '/static/'
        WSGI_APPLICATION = 'settings.wsgi.application'

    class Error(Exception):
        pass

    stub.apply({
        'django.core.management.base': {
            'CommandError': Error,
            'BaseCommand': '[cls]',
        },
        'django.conf.settings': Settings,
    })

    fifofile = tmpdir.join('some.fifo')
    fifofile.write('')

    monkeypatch.setattr(
        'uwsgiconf.contrib.django.uwsgify.toolbox.SectionMutator.get_fifo_filepath',
        lambda project_name: '%s' % fifofile)


def test_mutate_existing_section(patch_base_command):
    from uwsgiconf.contrib.django.uwsgify.toolbox import SectionMutator

    mutator = SectionMutator.spawn(dir_base=os.path.dirname(__file__))
    assert mutator.section.name == 'testdummy'


def test_uwsgi_run(monkeypatch, patch_project_dir, stub):

    class Settings(object):

        MEDIA_URL = '/static/media/'
        MEDIA_ROOT = '/dummy/media/'
        STATIC_URL = '/static/'
        STATIC_ROOT = '/dummy/static/'
        WSGI_APPLICATION = 'settings.wsgi.application'

    stub.apply({
        'django.core.management.call_command': '[func]',
        'django.core.management.base.BaseCommand': '[cls]',
        'django.conf.settings': Settings,
    })

    monkeypatch.setattr('os.execvp', lambda *args, **kwargs: None)

    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_run import Command

    Command().handle(
        compile=False,
        contribute_static=True,
        contribute_runtimes=True,
        contribute_errpages=True,
        embedded=False,
    )
    Command().handle(compile=True, embedded=False)

    with pytest.raises(ImportError):  # py3 - ModuleNotFoundError
        Command().handle(compile=False, contribute_static=True, embedded=True)


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


def test_uwsgi_sysinit_systemd(patch_base_command, capsys):
    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_sysinit import Command

    Command().handle(
        systype='systemd', nostatic=True, noruntimes=True)

    out, err = capsys.readouterr()

    uid = os.getuid()

    assert not err
    assert ('-o %s -g %s' % (uid, os.getgid())) in out
    assert ('/run/user/%s/dummy' % uid) in out
    assert 'Description=dummy uWSGI Service' in out
    assert 'bin/python' in out
    assert 'dummy/manage.py uwsgi_run --nostatic --noruntimes\n' in out


def test_uwsgi_sysinit_upstart(patch_base_command, capsys):
    from uwsgiconf.contrib.django.uwsgify.management.commands.uwsgi_sysinit import Command

    Command().handle(
        systype='upstart', nostatic=True)

    out, err = capsys.readouterr()

    assert not err
    assert 'description "dummy uWSGI Service"' in out
    assert 'bin/python' in out
    assert 'dummy/manage.py uwsgi_run' in out
