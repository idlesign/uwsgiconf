import os
from pathlib import Path

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
        lambda project_name: Path(f'{fifofile}'))


def test_mutate_existing_section(patch_base_command):
    from uwsgiconf.contrib.django.uwsgify.toolbox import SectionMutator

    mutator = SectionMutator.spawn(dir_base=Path(__file__).parent.parent)
    assert mutator.section.name == 'testdummy'


def test_uwsgi_run(monkeypatch, patch_project_dir, command_run, settings, tmpdir, capsys):

    from django.core.files.storage import storages
    storages['staticfiles'].location = f'{tmpdir}'  # prevent hitting cache

    def runtime_dir(self):
        return Path(f'{tmpdir}')

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

    with pytest.raises(ImportError, match="No module named 'pyuwsgi"):
        command_run('uwsgi_run', options={'embedded': True})
    out, err = capsys.readouterr()
    assert 'Deleting' in out


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
    assert f'-o {uid} -g {os.getgid()}' in out
    assert f'/run/user/{uid}/dummy' in out
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

