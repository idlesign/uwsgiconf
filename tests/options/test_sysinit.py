import os

from uwsgiconf.presets.nice import PythonSection
from uwsgiconf.sysinit import get_config


def test_sysinit_systemd():

    section = PythonSection()
    config = get_config('systemd', conf=section, conf_path='/some/path')

    assert ('-o %s -g %s' % (os.getuid(), os.getgid())) in config
    assert 'run /some/path' in config
    assert 'Description=some uWSGI Service' in config

    section.main_process.set_owner_params(uid=9999, gid=9999)
    config = get_config('systemd', conf=section, conf_path='/some/path')
    assert '-o 9999 -g 9999' in config


def test_sysinit_upstart():

    section = PythonSection()

    config = get_config('upstart', conf=section, conf_path='/other/path')

    assert 'run /other/path' in config
    assert 'description "other uWSGI Service"' in config


