from uwsgiconf import Section


def test_main_process_basics(assert_lines):

    assert_lines([
        'touch-reload = /here/a',
    ], Section().grp_main_process.set_basic_params(touch_reload='/here/a'))

    assert_lines([
        'pidfile = /here/file',
    ], Section().grp_main_process.set_pid_file('/here/file'))

    assert_lines([
        'safe-pidfile2 = /here/file',
    ], Section().grp_main_process.set_pid_file(
        '/here/file', before_priv_drop=False, safe=True))

    assert_lines([
        'auto-procname = true',
    ], Section().grp_main_process.set_naming_params(autonaming=True))

    assert_lines([
        'uid = 1001',
    ], Section().grp_main_process.set_owner_params(uid=1001))

    assert_lines([
        'exec-asap = date',
    ], Section().grp_main_process.run_command_on_event('date'))

    assert_lines([
        'touch-exec = myfile.txt date',
    ], Section().grp_main_process.run_command_on_touch('date', 'myfile.txt'))

    assert_lines([
        'reload-mercy = 10',
    ], Section().grp_main_process.set_reload_params(mercy=10))
