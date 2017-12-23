from .. import uwsgi
from ..exceptions import UwsgiconfException
from ..utils import string_types, get_logger

_LOG = get_logger(__name__)


def get_available_num():
    """Returns first available signal number.

    :rtype: int

    :raises UwsgiconfException: If no signal is available.

    """
    for signum in range(0, 256):
        if not uwsgi.signal_registered(signum):
            return signum

    raise UwsgiconfException('No uWSGI signals available.')


def get_last_received():
    """Get the last signal received.

    :rtype: Signal
    """
    return Signal(uwsgi.signal_received())


class Signal(object):
    """Represents uWSGI signal."""

    __slots__ = ['num']

    def __init__(self, num=None):
        """
        :param int num: Signal number (0-256).

            .. note:: If not set it will be chosen automatically.

        """
        self.num = num or get_available_num()

    def __int__(self):
        return self.num

    def register_handler(self, target=None):
        """Decorator for a function to be used as a signal handler.

        :param str|unicode target: Where this signal will be delivered to. Default: ``worker``.

            * ``workers``  - run the signal handler on all the workers
            * ``workerN`` - run the signal handler only on worker N
            * ``worker``/``worker0`` - run the signal handler on the first available worker
            * ``active-workers`` - run the signal handlers on all the active [non-cheaped] workers

            * ``mules`` - run the signal handler on all of the mules
            * ``muleN`` - run the signal handler on mule N
            * ``mule``/``mule0`` - run the signal handler on the first available mule

            * ``spooler`` - run the signal on the first available spooler
            * ``farmN/farm_XXX``  - run the signal handler in the mule farm N or named XXX

            * http://uwsgi.readthedocs.io/en/latest/Signals.html#signals-targets

        """
        target = target or 'worker'
        sign_num = self.num

        def wrapper(func):

            _LOG.debug("Registering '%s' as signal '%s' handler ...", func.__name__, sign_num)

            uwsgi.register_signal(sign_num, target, func)

            return func

        return wrapper

    def send(self, remote=''):
        """Sends the signal to master or remote.

        :param str|unicode remote: Remote address.

        :rtype: None

        :raises ValueError: If remote rejected the signal.

        :raises IOError: If unable to deliver to remote.
        """
        uwsgi.signal(self.num, remote)

    def wait(self):
        """Waits for the given of any signal.

        Block the process/thread/async core until a signal is received. Use signal_received to get the number of
        the signal received. If a registered handler handles a signal, signal_wait will be interrupted and the actual
        handler will handle the signal.

        * http://uwsgi-docs.readthedocs.io/en/latest/Signals.html#signal-wait-and-signal-received

        :raises SystemError: If something went wrong.
        """
        uwsgi.signal_wait(self.num)


def _automate_signal(target, func):

    if target is None or isinstance(target, string_types):
        sig = Signal()

        func(sig)

        return sig.register_handler(target=target)

    func(target)
