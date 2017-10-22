from uwsgiconf.runtime.signals import *
from uwsgiconf.runtime.scheduling import register_timer


def test_signals():

    available = get_available_num()
    latest = get_last_received()

    sig = Signal()

    @sig.register_handler()
    def signalled():
        pass

    sig.send()
    sig.wait()

    @sig.register_handler()
    def my(sign):
        pass

    register_timer(3, sig)
