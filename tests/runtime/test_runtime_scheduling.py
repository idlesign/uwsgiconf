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
