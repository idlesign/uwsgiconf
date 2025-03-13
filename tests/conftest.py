import os
import subprocess
from os import environ

import pytest

from uwsgiconf.emulator.signals import cleanup as cleanup_emu_signals
from uwsgiconf.runtime.signals import REGISTERED_SIGNALS
from uwsgiconf.settings import ENV_FORCE_STUB, ENV_MAINTENANCE_INPLACE, ENV_MAINTENANCE

# Force stub to allow shallow testing.
environ[ENV_FORCE_STUB] = '1'

from pytest_djangoapp import configure_djangoapp_plugin


pytest_plugins = configure_djangoapp_plugin(
    {
        'ROOT_URLCONF': 'tests.contrib.urls',
        'WSGI_APPLICATION': 'tests.contrib.app',
        'STATIC_ROOT': 'replaceit/',
        'CACHES': {
            "default": {
                "BACKEND": "uwsgiconf.contrib.django.uwsgify.cache.UwsgiCache",
                "LOCATION": "mycache",
            }
        }
    },
    app_name='uwsgiconf.contrib.django.uwsgify',
    extend_MIDDLEWARE=[
        # messages in admin support
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
    extend_INSTALLED_APPS=[
        'django.contrib.staticfiles',
    ],
    admin_contrib=True,
)


@pytest.fixture(scope='session')
def ini():

    def wrapped(section, stamp):
        return section.as_configuration().format(stamp=stamp)

    return wrapped


@pytest.fixture(scope='session')
def assert_lines(ini):

    def wrapped(lines, source, assert_in=True, stamp=False):
        source = ini(source, stamp)

        if not isinstance(lines, list):
            lines = [lines]

        for line in lines:
            if assert_in:
                assert line in source, source
            else:
                assert line not in source, source

    return wrapped


@pytest.fixture
def mock_popen(monkeypatch):

    def mock(func_communicate):

        class MockPopen(object):

            def __init__(self, *args, **kwargs):
                pass

            def communicate(self, *args, **kwargs):
                return func_communicate(*args, **kwargs)

        monkeypatch.setattr(subprocess, 'Popen', MockPopen)

    return mock


@pytest.fixture(autouse=True)
def cleanup():
    os.environ.pop(ENV_MAINTENANCE, None)
    os.environ.pop(ENV_MAINTENANCE_INPLACE, None)
    REGISTERED_SIGNALS.clear()
    cleanup_emu_signals()
