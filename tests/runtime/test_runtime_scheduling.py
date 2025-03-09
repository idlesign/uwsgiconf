import freezegun
import pytest

from uwsgiconf.runtime.scheduling import *


def test_timers():

    results = []

    @register_timer(20)
    def timer_1():
        results.append('timer')

    @register_timer_rb(3)
    def timer_2():
        results.append('rb')

    @register_timer_ms(200)
    def timer_3():
        results.append('ms')

    # check seamless function execution
    timer_1()
    timer_2()
    timer_3()

    assert results == ['timer', 'rb', 'ms']


@freezegun.freeze_time('2025-02-05 15:00:00')
def test_cron():

    results = []

    @register_cron(hour=-3)
    def fire1(sig):
        results.append('fire1')

    with pytest.raises(RuntimeConfigurationError, match='String cron rule without a range'):
        register_cron(hour='-%s/2')

    @register_cron(hour='15-18/2', weekday='0-6')
    def runnable1(sig):
        results.append('runnable1')

    @register_cron(hour='15-18')
    def runnable2(sig):
        results.append('runnable2')

    @register_cron(hour='12-14')
    def not_runnable(sig):
        results.append('not_runnable')

    fire1(0)
    runnable1(0)
    runnable2(0)
    not_runnable(0)

    assert results == ['fire1', 'runnable1', 'runnable2']
