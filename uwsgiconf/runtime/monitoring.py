from .signals import _automate_signal
from .. import uwsgi


def register_file_monitor(filename, signal_or_target=None):
    """Maps a specific file/directory modification event to a signal.

    :param str|unicode filename: File or a directory to watch for its modification.

    :param int|Signal|str|unicode signal_or_target: Existing signal to raise
        or Signal Target to register signal implicitly.

    :raises ValueError: If unable to register monitor.
    """
    return _automate_signal(signal_or_target, func=lambda sig: uwsgi.add_file_monitor(int(sig), filename))


class Metric(object):
    """User metric related stuff."""

    @classmethod
    def get(cls, key):
        """Returns metric value by key.

        :param str|unicode key:

        :rtype: int|long
        """
        return uwsgi.metric_get(key)

    @classmethod
    def metric_set(cls, key, value, mode=None):
        """Sets metric value.

        :param str|unicode key:

        :param int|long value:

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

        return func(key, value)

    @classmethod
    def incr(cls, key, delta=1):
        """Increments the specified metric key value by the specified value.

        :param str|unicode key:

        :param int delta:

        :rtype: bool
        """
        return uwsgi.metric_inc(key, delta)

    @classmethod
    def decr(cls, key, delta=1):
        """Decrements the specified metric key value by the specified value.

        :param str|unicode key:

        :param int delta:

        :rtype: bool
        """
        return uwsgi.metric_dec(key, delta)

    @classmethod
    def mul(cls, key, value=1):
        """Multiplies the specified metric key value by the specified value.

        :param str|unicode key:

        :param int value:

        :rtype: bool
        """
        return uwsgi.metric_mul(key, value)

    @classmethod
    def div(cls, key, value=1):
        """Divides the specified metric key value by the specified value.

        :param str|unicode key:

        :param int value:

        :rtype: bool
        """
        return uwsgi.metric_div(key, value)
