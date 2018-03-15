import pytest

from uwsgiconf.runtime.scheduling import *


def test_timers():

    @register_timer(20)
    def fire1():
        pass

    @register_timer_rb(3)
    def fire2():
        pass


def test_cron():

    @register_cron(hour=-3)
    def fire1():
        pass

    with pytest.raises(RuntimeConfigurationError):
        register_cron(hour='-%s/2')

    now = datetime.now()

    @register_cron(hour='%s-%s/2' % (now.hour, now.hour+3), weekday='0-6')
    def runnable1():
        return 100

    @register_cron(hour='%s-%s' % (now.hour, now.hour+3))
    def runnable2():
        return 200

    @register_cron(hour='%s-%s' % (now.hour-3, now.hour-1))
    def not_runnable():
        return 200

    assert runnable1() == 100
    assert runnable2() == 200
    assert not_runnable() is None
