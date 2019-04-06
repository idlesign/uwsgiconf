from uwsgiconf.runtime.alarms import *
from uwsgiconf.runtime.asynced import *
from uwsgiconf.runtime.control import *
from uwsgiconf.runtime.environ import *
from uwsgiconf.runtime.logging import *
from uwsgiconf.runtime.request import *
from uwsgiconf.runtime.websockets import *


def test_harakiri_imposed():

    @harakiri_imposed(1)
    def doomed():
        pass

    doomed()

    with harakiri_imposed(1):
        pass
