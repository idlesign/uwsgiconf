from collections.abc import Callable
from typing import NamedTuple

from .. import uwsgi
from ..exceptions import UwsgiconfException
from ..settings import get_maintenance_inplace
from ..utils import get_logger
from .mules import Farm, Mule, TypeMuleFarm

_LOG = get_logger(__name__)


class SignalDescription(NamedTuple):
    """Registered signal information."""

    num: int
    """Signal number."""

    target: str
    """Target: worker, mule, etc."""

    func: Callable
    """Function to run on signal."""


REGISTERED_SIGNALS: dict[int, SignalDescription] = {}
"""Registered signals."""


def get_available_num() -> int:
    """Returns first available signal number.

    :raises UwsgiconfException: If no signal is available.

    """
    for signum in range(256):
        if not uwsgi.signal_registered(signum):
            return signum

    raise UwsgiconfException('No uWSGI signals available.')


def get_last_received() -> 'Signal':
    """Get the last signal received."""
    num = uwsgi.signal_received()
    # uWSGI returns `0` both for Signal 0 and if thera was no signal
    return REGISTERED_SIGNALS.get(num, Signal(num))


class Signal:
    """Represents uWSGI signal.

    .. warning:: If you define a new function in worker1 and register
        it as a signal handler, only worker1 can run it. The best way to register signals
        is defining them in the master (.runtime.uwsgi.postfork_hooks.add), so all workers see them.

    .. code-block:: python

        signal = Signal()

        @signal.register_handler()
        def somefunc():
            pass

        # or the same:

        @signal
        def somefunc():
            pass

    """
    __slots__ = ['num']

    def __init__(self, num: int | None = None):
        """
        :param int num: Signal number (0-255).

            .. note:: If not set it will be chosen automatically.

        """
        if num is None:
            num = get_available_num()
        self.num = num

    def __int__(self):
        return self.num

    def __call__(self, func: Callable):
        # Allows using object as a decorator.
        return self.register_handler()(func)

    @property
    def registered(self) -> bool:
        """Whether the signal is registered."""
        return bool(uwsgi.signal_registered(self.num))

    def register_handler(
            self,
            *,
            target: 'TypeTarget' = None,
            callback: Callable[['Signal'], None] | None = None
    ) -> Callable:
        """Decorator for a function to be used as a signal handler.

        .. code-block:: python

            signal = Signal()

            @signal.register_handler()
            def somefunc():
                pass

        :param target: Where this signal will be delivered to. Default: ``worker``.

            * Mule / Farm object - run on a certain mule or a farm.
            * ``workers``  - run the signal handler on all the workers
            * ``workerN`` - run the signal handler only on worker N
            * ``worker``/``worker0`` - run the signal handler on the first available worker
            * ``active-workers`` - run the signal handlers on all the active [non-cheaped] workers

            * ``mules`` - run the signal handler on all the mules
            * ``muleN`` - run the signal handler on mule N
            * ``mule``/``mule0`` - run the signal handler on the first available mule

            * ``spooler`` - run the signal on the first available spooler
            * ``farmN/farm_XXX``  - run the signal handler in the mule farm N or named XXX

            * http://uwsgi.readthedocs.io/en/latest/Signals.html#signals-targets

        :param callback: Function to be called after the registration.

        """
        target = target or 'worker'

        if isinstance(target, Mule):
            target = f'mule{target.id}'

        elif isinstance(target, Farm):
            target = f'farm_{target.name}'

        sign_num = self.num

        def wrapper(func: Callable):

            _LOG.debug(f"Registering '{func.__name__}' as signal '{sign_num}' handler ...")

            uwsgi.register_signal(sign_num, target, func)
            callback and callback(self)
            REGISTERED_SIGNALS[sign_num] = SignalDescription(sign_num, target, func)

            return func

        return wrapper

    def send(self, *, remote: str | None = None):
        """Sends the signal to master or remote.

        When you send a signal, it is copied into the master's queue.
        The master will then check the signal table and dispatch the messages.

        :param remote: Remote address.

        :raises ValueError: If remote rejected the signal.

        :raises OSError: If unable to deliver to remote.

        """
        uwsgi.signal(self.num, *([remote] if remote is not None else []))

    def wait(self):
        """Waits for the given of any signal.

        Block the process/thread/async core until a signal is received. Use signal_received to get the number of
        the signal received. If a registered handler handles a signal, signal_wait will be interrupted and the actual
        handler will handle the signal.

        * http://uwsgi-docs.readthedocs.io/en/latest/Signals.html#signal-wait-and-signal-received

        :raises SystemError: If something went wrong.

        """
        uwsgi.signal_wait(self.num)


TypeTarget = Signal | TypeMuleFarm | None


def _automate_signal(target: TypeTarget, func: Callable):
    """
    :param target:
    :param func: wrapper for uwsgi signal related function (e.g. add_timer())
    """
    if get_maintenance_inplace():
        # Prevent background works in maintenance mode.
        return lambda *args, **kwarg: None

    if target is None or isinstance(target, str | Mule | Farm):
        return Signal().register_handler(target=target, callback=func)

    # Signal instance passed
    func(target)
