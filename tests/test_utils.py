import os

import pytest

from uwsgiconf.utils import UwsgiRunner, parse_command_plugins_output, ConfModule, get_uwsgi_stub_attrs_diff, \
    filter_locals
from uwsgiconf.exceptions import UwsgiconfException


SAMPLE_OUT_PLUGINS_MANY = b'''

*** uWSGI loaded generic plugins ***
gevent
syslog
stats_pusher_socket

*** uWSGI loaded request plugins ***
0: python
173: rpc
--- end of plugins list ---

*** Starting uWSGI 2.0.15 (64bit) on [Fri Jul 28 20:05:53 2017] ***
compiled with version: 6.3.0 20170406 on 28 July 2017 20:04:29
'''

SAMPLE_OUT_PLUGINS_EMPTY = b'''

*** uWSGI loaded generic plugins ***

*** uWSGI loaded request plugins ***
--- end of plugins list ---

*** Starting uWSGI 2.0.14-debian (64bit) on [Fri Jul 28 20:09:00 2017] ***
compiled with version: 6.3.0 20170221 on 27 February 2017 15:11:38
'''


def test_filter_locals():

    fake_locals = {'a': 1, 'b': 2, 'c': 3}

    assert filter_locals(fake_locals, drop=['a', 'c']) == {'b': 2}
    assert filter_locals(fake_locals, include=['a', 'b']) == {'a': 1, 'b': 2}
    assert filter_locals(fake_locals, include=['a', 'b'], drop=['b']) == {'a': 1}


def test_parser():
    plugins = parse_command_plugins_output(SAMPLE_OUT_PLUGINS_MANY.decode())

    assert len(plugins.generic) == 3
    assert len(plugins.request) == 2
    assert 'rpc' in plugins.request

    plugins = parse_command_plugins_output(SAMPLE_OUT_PLUGINS_EMPTY.decode())
    assert len(plugins.generic) == 0
    assert len(plugins.request) == 0


def test_runner(mock_popen):

    mock_popen(lambda: (SAMPLE_OUT_PLUGINS_MANY, ''))

    runner = UwsgiRunner()
    plugins = runner.get_plugins()
    assert len(plugins.generic) == 3
    assert len(plugins.request) == 2


def test_conf_module_compile():
    fpath = os.path.join(os.path.dirname(__file__), 'confs', 'dummy.py')

    # invalid objects
    module = ConfModule(fpath)
    assert module.configurations
    assert len(module.configurations) == 2

    out = []
    for conf in module.configurations:
        out.append(conf.format())

    out = '\n'.join(out)

    assert '[uwsgi]' in out
    assert '[conf1_2]' in out
    assert 'D=E' in out


def test_conf_module_run(monkeypatch):
    executed = []
    monkeypatch.setattr(os, 'spawnvp', lambda *args: executed.append(True))

    module = ConfModule(os.path.join(os.path.dirname(__file__), 'confs', 'dummy.py'))
    module.spawn_uwsgi()

    assert len(executed) == 2
    assert all(executed)

    executed = []
    monkeypatch.setattr(os, 'execvp', lambda *args: executed.append(True))

    module = ConfModule(os.path.join(os.path.dirname(__file__), 'confs', 'dummyone.py'))
    module.spawn_uwsgi()

    assert len(executed) == 1
    assert all(executed)


def test_get_uwsgi_stub_attrs_diff():

    with pytest.raises(UwsgiconfException):
        get_uwsgi_stub_attrs_diff()  # uwsgi is unavailable

    import sys

    sys.modules['uwsgi'] = type('DummyModule', (object,), {'dummy_uwsgi': True})

    from_candidate, from_stub = get_uwsgi_stub_attrs_diff()

    assert from_candidate == ['dummy_uwsgi']
    assert from_stub

    del sys.modules['uwsgi']
