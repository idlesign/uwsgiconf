from uwsgiconf.runtime.alarms import *
from uwsgiconf.runtime.async import *
from uwsgiconf.runtime.caching import *
from uwsgiconf.runtime.control import *
from uwsgiconf.runtime.environ import *
from uwsgiconf.runtime.locking import *
from uwsgiconf.runtime.logging import *
from uwsgiconf.runtime.monitoring import *
from uwsgiconf.runtime.mules import *
from uwsgiconf.runtime.request import *
from uwsgiconf.runtime.rpc import *
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


def test_caching():

    cache = Cache('mine')
    assert cache.get('some', 'other') == 'other'


def test_locking():

    @lock()
    def locked():
        pass

    locked()

    with lock():
        pass


def test_rpc():

    @register_rpc()
    def expose_me():
        pass

    make_rpc_call('expose_me')


def test_signals():

    sig = Signal()

    @sig.register_handler()
    def signalled():
        pass


def test_monitoring():

    @register_file_monitor('/here/there.file')
    def handle_file_modification(sig_num):
        pass
