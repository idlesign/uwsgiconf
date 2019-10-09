from .. import uwsgi


connect = uwsgi.async_connect
"""Issues socket connection. And returns a file descriptor.

* http://uwsgi.readthedocs.io/en/latest/Async.html

:param str|unicode socket:

:rtype: int
"""

sleep = uwsgi.async_sleep
"""Suspends handling the current request and passes control to the next async core.

* http://uwsgi.readthedocs.io/en/latest/Async.html

:param seconds: Sleep time, in seconds.

:rtype None:
"""

suspend = uwsgi.suspend
"""Suspends handling of current coroutine/green thread and passes control
to the next async core.

* http://uwsgi.readthedocs.io/en/latest/Async.html#suspend-resume

:rtype: bool
"""

get_loop_name = uwsgi.loop
"""Returns current event loop name or None if loop is not set.

:rtype: st|unicode|None
"""

wait_for_fd_read = uwsgi.wait_fd_read
"""Suspends handling of the current request until there is something
to be read on file descriptor.

May be called several times before yielding/suspending
to add more file descriptors to the set to be watched.

* http://uwsgi-docs.readthedocs.io/en/latest/Async.html#waiting-for-i-o

:param int fd: File descriptor number.

:param int timeout: Timeout. Default:  infinite.

:rtype: bytes|str

:raises IOError: If unable to read.
"""

wait_for_fd_write = uwsgi.wait_fd_write
"""Suspends handling of the current request until there is nothing more
to be written on file descriptor.

May be called several times to add more file descriptors to the set to be watched.

* http://uwsgi-docs.readthedocs.io/en/latest/Async.html#waiting-for-i-o

:param int fd: File descriptor number.

:param int timeout: Timeout. Default:  infinite.

:rtype: bytes|str

:raises IOError: If unable to read.
"""
