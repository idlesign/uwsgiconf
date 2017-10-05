from uwsgiconf.config import Section


def test_empire_basics(assert_lines):

    assert_lines([
        'emperor = /myvassals',
    ], Section().empire.set_emperor_params(vassals_home='/myvassals'))

    assert_lines([
        'imperial-monitor-list = true',
    ], Section().empire.print_monitors())

    assert_lines([
        'emperor-command-socket = /mysock',
    ], Section().empire.set_emperor_command_params('/mysock'))

    assert_lines([
        'emperor-wrapper = myvas',
    ], Section().empire.set_vassals_wrapper_params('myvas'))

    assert_lines([
        'emperor-throttle = 100',
    ], Section().empire.set_throttle_params(100))

    assert_lines([
        'emperor-required-heartbeat = 200',
    ], Section().empire.set_tolerance_params(200))

    assert_lines([
        'emperor-tyrant = true',
    ], Section().empire.set_mode_tyrant_params(enable=True))

    assert_lines([
        'emperor-broodlord = 40',
    ], Section().empire.set_mode_broodlord_params(40))
