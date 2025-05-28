from uwsgiconf.runtime.scheduling import register_timer
from uwsgiconf.runtime.signals import Signal, get_available_num, get_last_received


def test_signals():

    assert get_available_num() == 0
    assert get_last_received().num == 0

    sig = Signal()
    results = []

    # register first handler
    @sig.register_handler()
    def signalled(sig):
        results.append('signalled')

    assert get_available_num() == 1

    # send the signal
    sig.send()
    sig.wait()

    # change handler
    @sig.register_handler()
    def my(sig):
        results.append('my')

    # register a timer for the signal
    register_timer(3, target=sig)

    sig.send()
    assert results == ['signalled', 'my']
