from .signals import _automate_signal
from .. import uwsgi


# todo: add_ms_timer


def register_timer(period, target=None):
    """Add timer.

    Can be used as a decorator:

        .. code-block:: python

            @register_timer(3)
            def repeat():
                do()

    :param int period: The interval (seconds) at which to raise the signal.

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

    :rtype: bool|callable

    :raises ValueError: If unable to add timer.
    """
    return _automate_signal(target, func=lambda sig: uwsgi.add_timer(int(sig), period))


def register_timer_rb(period, repeat=None, target=None):
    """Add a red-black timer (based on black-red tree).

        .. code-block:: python

            @register_timer_rb(3)
            def repeat():
                do()

    :param int period: The interval (seconds) at which the signal is raised.

    :param int repeat: How many times to repeat. Default: None - infinitely.

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

    :rtype: bool|callable

    :raises ValueError: If unable to add timer.
    """
    return _automate_signal(target, func=lambda sig: uwsgi.add_rb_timer(int(sig), period, repeat or 0))


def register_cron(weekday=None, month=None, day=None, hour=None, minute=None, target=None):
    """Adds cron. The interface to the uWSGI signal cron facility.

        .. code-block:: python

            @register_cron(hour=-3)  # Every 3 hours.
            def repeat():
                do()

    .. note:: Arguments work similarly to a standard crontab,
        but instead of "*", use -1,
        and instead of "/2", "/3", etc. use -2 and -3, etc.

    :param int weekday: Day of a the week number. Defaults to `each`.
        0 - Sunday  1 - Monday  2 - Tuesday  3 - Wednesday
        4 - Thursday  5 - Friday  6 - Saturday

    :param int month: Month number 1-12. Defaults to `each`.

    :param int day: Day of the month number 1-31. Defaults to `each`.

    :param int hour: Hour 0-23. Defaults to `each`.

    :param int minute: Minute 0-59. Defaults to `each`.

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

    :rtype: bool|callable

    :raises ValueError: If unable to add cron rule.
    """
    args = [(-1 if arg is None else arg) for arg in (minute, hour, day, month, weekday)]

    return _automate_signal(target, func=lambda sig: uwsgi.add_cron(int(sig), *args))