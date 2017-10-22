from uwsgiconf.runtime.alarms import *
from uwsgiconf.runtime.async import *
from uwsgiconf.runtime.control import *
from uwsgiconf.runtime.environ import *
from uwsgiconf.runtime.locking import *
from uwsgiconf.runtime.logging import *
from uwsgiconf.runtime.request import *
from uwsgiconf.runtime.scheduling import *
from uwsgiconf.runtime.signals import *
from uwsgiconf.runtime.websockets import *


def test_harakiri_imposed():

    @harakiri_imposed(1)
    def doomed():
        pass

    doomed()

    with harakiri_imposed(1):
        pass


def test_locking():

    @lock()
    def locked():
        pass

    locked()

    with lock():
        pass


def test_signals():

    sig = Signal()

    @sig.register_handler()
    def signalled():
        pass
