from uwsgiconf import Section


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
        'alarm = my cmd:some',
    ], alarms.register_alarm(alarms.cls_alarm_command('my', 'some')))

    alarms = Section().alarms
    assert_lines([
        'alarm = mysig signal:17',
    ], alarms.register_alarm(alarms.cls_alarm_signal('mysig', 17)))

    alarms = Section().alarms
    assert_lines([
        'alarm = tomule mule:2',
    ], alarms.register_alarm(alarms.cls_alarm_mule('tomule', 2)))

    alarms = Section().alarms
    assert_lines([
        'plugin = alarm_curl',
        'alarm = test2 curl:http://192.168.173.6:9191/argh;auth_pass=foobar;auth_user=topogigio',
    ], alarms.register_alarm(
        alarms.cls_alarm_curl(
            'test2', 'http://192.168.173.6:9191/argh',
            auth_user='topogigio', auth_pass='foobar')))

    alarms = Section().alarms
    assert_lines([
        'plugin = alarm_xmpp',
        'alarm = jab xmpp:idle@some.com;12345;one@some.com,two@some.com',
    ], alarms.register_alarm(
        alarms.cls_alarm_xmpp('jab', 'idle@some.com', '12345', ['one@some.com', 'two@some.com'])))


def test_alarms_on_log(assert_lines):

    alarms = Section().alarms

    alarm1 = alarms.cls_alarm_command('mycom', 'some')
    alarm2 = alarms.cls_alarm_signal('mysig', 27)

    assert_lines([
        'alarm = mycom cmd:some',
        'alarm = mysig signal:27',
        'alarm-log = mycom,mysig some text',
    ], alarms.alarm_on_log([alarm1, alarm2], 'some text'))

    assert_lines([
        'not-alarm-log = mycom other',
    ], alarms.alarm_on_log(alarm1, 'other', skip=True))

