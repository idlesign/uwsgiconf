from uwsgiconf.config import Section


def test_alarms_basics(assert_lines):

    assert_lines([
        'alarm-msg-size = 10000',
    ], Section().alarms.set_basic_params(msg_size=10000))

    assert_lines([
        'alarm-list = true',
    ], Section().alarms.print_alarms())


def test_alarms_registration(assert_lines):

    alarms = Section().alarms
    assert_lines([
        'alarm = my log:',
    ], alarms.register_alarm(alarms.alarm_types.log('my')))

    alarms = Section().alarms
    assert_lines([
        'alarm = my cmd:some',
    ], alarms.register_alarm(alarms.alarm_types.command('my', 'some')))

    alarms = Section().alarms
    assert_lines([
        'alarm = mysig signal:17',
    ], alarms.register_alarm(alarms.alarm_types.signal('mysig', 17)))

    alarms = Section().alarms
    assert_lines([
        'alarm = tomule mule:2',
    ], alarms.register_alarm(alarms.alarm_types.mule('tomule', 2)))

    alarms = Section().alarms
    assert_lines([
        'plugin = alarm_curl',
        'alarm = test2 curl:http://192.168.173.6:9191/argh;auth_pass=foobar;auth_user=topogigio',
    ], alarms.register_alarm(
        alarms.alarm_types.curl(
            'test2', 'http://192.168.173.6:9191/argh',
            auth_user='topogigio', auth_pass='foobar')))

    alarms = Section().alarms
    assert_lines([
        'plugin = alarm_xmpp',
        'alarm = jab xmpp:idle@some.com;12345;one@some.com,two@some.com',
    ], alarms.register_alarm(
        alarms.alarm_types.xmpp('jab', 'idle@some.com', '12345', ['one@some.com', 'two@some.com'])))


def test_alarms_on_log(assert_lines):

    alarms = Section().alarms

    alarm1 = alarms.alarm_types.command('mycom', 'some')
    alarm2 = alarms.alarm_types.signal('mysig', 27)

    assert_lines([
        'alarm = mycom cmd:some',
        'alarm = mysig signal:27',
        'alarm-log = mycom,mysig some text',
    ], alarms.alarm_on_log([alarm1, alarm2], 'some text'))

    assert_lines([
        'not-alarm-log = mycom other',
    ], alarms.alarm_on_log(alarm1, 'other', skip=True))


def test_alarms_on_fd(assert_lines):

    alarms = Section().alarms
    alarm1 = alarms.alarm_types.signal('mysig', 27)
    alarm2 = alarms.alarm_types.signal('some', 17)

    assert_lines([
        'alarm = mysig signal:27',
        'alarm = some signal:17',
        'alarm-fd = mysig $(CGROUP_OOM_FD):8 damn it!',
        'alarm-fd = some $(CGROUP_OOM_FD):8 damn it!',
    ], alarms.alarm_on_fd_ready([alarm1, alarm2], '$(CGROUP_OOM_FD)', 'damn it!', byte_count=8))


def test_alarms_on_queue(assert_lines):

    alarms = Section().alarms
    alarm1 = alarms.alarm_types.signal('mysig', 27)
    alarm2 = alarms.alarm_types.signal('some', 17)

    assert_lines([
        'alarm = mysig signal:27',
        'alarm = some signal:17',
        'alarm-backlog = mysig',
        'alarm-backlog = some',
    ], alarms.alarm_on_queue_full([alarm1, alarm2]))


def test_alarms_on_segfault(assert_lines):

    alarms = Section().alarms
    alarm1 = alarms.alarm_types.signal('mysig', 27)
    alarm2 = alarms.alarm_types.signal('some', 17)

    assert_lines([
        'alarm = mysig signal:27',
        'alarm = some signal:17',
        'alarm-segfault = mysig',
        'alarm-segfault = some',
    ], alarms.alarm_on_segfault([alarm1, alarm2]))


