from functools import wraps
from .. import uwsgi


stop = uwsgi.stop
"""Stops uWSGI.

:rtype: bool|None
"""

reload = uwsgi.reload
"""Gracefully reloads uWSGI.

* http://uwsgi.readthedocs.io/en/latest/Management.html#reloading-the-server

:rtype: bool
"""

disconnect = uwsgi.disconnect
"""Drops current connection.

:rtype: None
"""

set_process_name = uwsgi.setprocname
"""Sets current process name.

:param str|unicode name:

:rtype: bool
"""


class harakiri_imposed(object):
    """Decorator and context manager.
    Allows temporarily setting harakiri timeout for a function or a code block.

    Examples:

        .. code-block:: python

            @harakiri_imposed(1)
            def doomed():
                do()


        .. code-block:: python

            with harakiri_imposed(10):
                do()

    """
    def __init__(self, timeout):
        """
        :param int timeout: Timeout (seconds) before harakiri.
        """
        self._timeout = timeout

    def __call__(self, func):
        timeout = self._timeout

        @wraps(func)
        def wrapped(*args, **kwargs):
            uwsgi.set_user_harakiri(timeout)

            try:
                result = func(*args, **kwargs)

            finally:
                uwsgi.set_user_harakiri(0)

            return result

        return wrapped

    def __enter__(self):
        uwsgi.set_user_harakiri(self._timeout)

    def __exit__(self, exc_type, exc_val, exc_tb):
        uwsgi.set_user_harakiri(0)
