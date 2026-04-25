from os import environ

import freezegun
import pytest

from uwsgiconf.exceptions import RuntimeConfigurationError
from uwsgiconf.runtime.mules import Farm, Mule
from uwsgiconf.runtime.scheduling import register_cron, register_timer, register_timer_ms, register_timer_rb
from uwsgiconf.runtime.signals import REGISTERED_SIGNALS, Signal


def test_timers():

    results = []

    mule = Mule(10)
    farm = Farm('myfa')

    @register_timer(20, target=mule)
    def timer_1():
        results.append('timer')

    @register_timer_rb(3, target=farm)
    def timer_2():
        results.append('rb')

    @register_timer_ms(200)
    def timer_3():
        results.append('ms')

    environ['UWSGICONF_SKIP_TASK_TIMER_NO_RUN'] = '1'

    @register_timer(2, target=farm)
    def timer_no_run():
        results.append('timernorun')

    # check seamless function execution
    timer_1()
    timer_2()
    timer_3()
    timer_no_run()  # won't run due to the flag in environ (see above)

    assert results == ['timer', 'rb', 'ms']

    # check targets
    signals = REGISTERED_SIGNALS
    assert signals[0].target == 'mule10'
    assert signals[1].target == 'farm_myfa'
    assert signals[2].target == 'worker'


@freezegun.freeze_time('2025-02-05 15:00:00')
def test_cron():

    results = []

    @register_cron(hour=-3)
    def fire1(sig):
        results.append('fire1')

    with pytest.raises(RuntimeConfigurationError, match='String cron rule without a range'):
        register_cron(hour='-%s/2')

    @register_cron(hour='15-18/2', weekday='0-6')
    def runnable1():  # run without passing signal number
        results.append('runnable1')

    @register_cron(hour='15-18')
    def runnable2():
        results.append('runnable2')

    @register_cron(hour='12-14')
    def not_runnable(sig):
        results.append('not_runnable')

    sig = Signal(0)

    @register_cron(target=sig)
    def fire2():
        results.append('fire2')

    fire1(0)
    sig.send()
    runnable1(0)
    runnable2()
    not_runnable(0)

    assert results == ['fire1', 'fire2', 'runnable1', 'runnable2']


@freezegun.freeze_time('2025-02-05 15:00:00')
def test_cron_zeros():

    results = []
    @register_cron(minute=0)
    def fire_zero():
        results.append('fire_zero')

    signals = REGISTERED_SIGNALS
    assert len(signals) == 1
    assert signals[0].func.params_hint == {'day': -1, 'hour': -1, 'minute': 0, 'month': -1, 'weekday': -1}
