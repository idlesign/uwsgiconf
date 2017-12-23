from .signals import _automate_signal
from .. import uwsgi


def register_file_monitor(filename, target=None):
    """Maps a specific file/directory modification event to a signal.

    :param str|unicode filename: File or a directory to watch for its modification.

    :param int|Signal|str|unicode target: Existing signal to raise
        or Signal Target to register signal implicitly.

        Available targets:

            * ``workers``  - run the signal handler on all the workers
            * ``workerN`` - run the signal handler only on worker N
            * ``worker``/``worker0`` - run the signal handler on the first available worker
            * ``active-workers`` - run the signal handlers on all the active [non-cheaped] workers

            * ``mules`` - run the signal handler on all of the mules
            * ``muleN`` - run the signal handler on mule N
            * ``mule``/``mule0`` - run the signal handler on the first available mule

            * ``spooler`` - run the signal on the first available spooler
            * ``farmN/farm_XXX``  - run the signal handler in the mule farm N or named XXX

    :raises ValueError: If unable to register monitor.
    """
    return _automate_signal(target, func=lambda sig: uwsgi.add_file_monitor(int(sig), filename))


class Metric(object):
    """User metric related stuff."""

    def __init__(self, name):
        """
        :param str|unicode name: Metric name.

        """
        self.name = name

    @property
    def value(self):
        """Current metric value.

        :rtype: int|long
        """
        return uwsgi.metric_get(self.name)

    def set(self, value, mode=None):
        """Sets metric value.

        :param int|long value: New value.

        :param str|unicode mode: Update mode.

            * None - Unconditional update.
            * max - Sets metric value if it is greater that the current one.
            * min - Sets metric value if it is less that the current one.

        :rtype: bool

        """
        if mode == 'max':
            func = uwsgi.metric_set_max

        elif mode == 'min':
            func = uwsgi.metric_set_min

        else:
            func = uwsgi.metric_set

        return func(self.name, value)

    def incr(self, delta=1):
        """Increments the specified metric key value by the specified value.

        :param int delta:

        :rtype: bool

        """
        return uwsgi.metric_inc(self.name, delta)

    def decr(self, delta=1):
        """Decrements the specified metric key value by the specified value.

        :param int delta:

        :rtype: bool

        """
        return uwsgi.metric_dec(self.name, delta)

    def mul(self, value=1):
        """Multiplies the specified metric key value by the specified value.

        :param int value:

        :rtype: bool

        """
        return uwsgi.metric_mul(self.name, value)

    def div(self, value=1):
        """Divides the specified metric key value by the specified value.

        :param int value:

        :rtype: bool
        """
        return uwsgi.metric_div(self.name, value)
