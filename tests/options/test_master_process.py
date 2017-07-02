import pytest

from uwsgiconf import Section
from uwsgiconf.exceptions import ConfigurationError



def test_master_process_basics(assert_lines):

    assert_lines([
        'master = true',
    ], Section().grp_master_process.set_basic_params(enabled=True))

    assert_lines([
        'smart-attach-daemon2 = /here/a.pid',
    ], Section().grp_master_process.attach_process(process_or_pid_path='/here/a.pid', background=False))

    assert_lines([
        'smart-attach-daemon = /here/a.pid',
    ], Section().grp_master_process.attach_process(process_or_pid_path='/here/a.pid', background=True))

    with pytest.raises(ConfigurationError):
        assert_lines([
            '',
        ], Section().grp_master_process.attach_process(process_or_pid_path='command', background=True))

    assert_lines([
        'attach-daemon = command',
    ], Section().grp_master_process.attach_process(process_or_pid_path='command', background=False))
