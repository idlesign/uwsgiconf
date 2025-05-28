from uwsgiconf.runtime.alarms import *  # noqa smoke
from uwsgiconf.runtime.asynced import *  # noqa smoke
from uwsgiconf.runtime.control import harakiri_imposed
from uwsgiconf.runtime.platform import uwsgi as platform  # noqa smoke
from uwsgiconf.runtime.logging import *  # noqa smoke
from uwsgiconf.runtime.request import *  # noqa smoke
from uwsgiconf.runtime.websockets import *  # noqa smoke


def test_harakiri_imposed():

    @harakiri_imposed(timeout=1)
    def doomed():
        pass

    doomed()

    with harakiri_imposed(timeout=1):
        pass
