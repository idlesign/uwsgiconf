from uwsgiconf import Section


def test_main_process_basics(assert_lines):

    assert_lines([
        'touch-reload = /here/a',
    ], Section().grp_main_process.set_basic_params(touch_reload='/here/a'))

    assert_lines([
        'pidfile = /here/file',
    ], Section().grp_main_process.set_pid_file('/here/file'))

    assert_lines([
        'auto-procname = true',
    ], Section().grp_main_process.set_naming_params(autonaming=True))

