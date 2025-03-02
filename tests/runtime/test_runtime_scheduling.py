import freezegun
import pytest

from uwsgiconf.runtime.scheduling import *
from uwsgiconf.runtime.signals import REGISTERED_SIGNALS


def test_timers():

    a = 1

    @register_timer(20)
    def timer_1():
        pass

    @register_timer_rb(3)
    def timer_2():
        pass

    @register_timer_ms(200)
    def timer_3():
        pass

    assert len(REGISTERED_SIGNALS) == 3
    assert REGISTERED_SIGNALS[0].func is timer_1


@freezegun.freeze_time('2025-02-05 15:00:00')
def test_cron():

    @register_cron(hour=-3)
    def fire1():
        pass

    with pytest.raises(RuntimeConfigurationError, match='String cron rule without a range'):
        register_cron(hour='-%s/2')

    @register_cron(hour='15-18/2', weekday='0-6')
    def runnable1():
        return 100

    @register_cron(hour='15-18')
    def runnable2():
        return 200

    @register_cron(hour='12-14')
    def not_runnable():
        return 200

    assert runnable1() == 100
    assert runnable2() == 200
    assert not_runnable() is None

    assert len(REGISTERED_SIGNALS) == 4
    assert REGISTERED_SIGNALS[0].func is fire1
