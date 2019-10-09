from threading import local

from .request import _Request
from .. import uwsgi as _uwsgi
from ..utils import decode_deep, decode


class _PostForkHooks(object):

    funcs = []

    @classmethod
    def add(cls):
        """Decorator. Registers a function to be called after process fork().

        :param callable func:
        """
        def add_(func):
            cls.funcs.append(func)
            return func
        return add_

    @classmethod
    def run(cls):
        """Runs registered hooks."""
        for func in cls.funcs:
            func()


_uwsgi.post_fork_hook = _PostForkHooks.run


class _Platform(object):

    request = _Request  # type: _Request
    """Current request information. 
    
    .. note:: Object is attached runtime.
    
    """

    postfork_hooks = _PostForkHooks
    """uWSGI is a preforking server, so you might need 
    to execute a fixup tasks (hooks) after each fork(). 
    Each hook will be executed in sequence on each process (worker/mule).
    
    .. note:: The fork() happen before app loading, so there's no hooks for dynamic apps.
        But one can still move postfork hooks in a .py file and 
        import it on server startup with `python.import_module()`.

    """

    workers_count = _uwsgi.numproc  # type: int
    """Number of workers (processes) currently running."""

    cores_count = _uwsgi.cores  # type: int
    """Detected number of processor cores."""

    buffer_size = _uwsgi.buffer_size  # type: int
    """The current configured buffer size in bytes."""

    threads_enabled = _uwsgi.has_threads  # type: bool
    """Flag indicating whether thread support is enabled."""

    started_on = _uwsgi.started_on  # type: int
    """uWSGI's startup Unix timestamp."""

    apps_map = _uwsgi.applications  # type: dict
    """Applications dictionary mapping mountpoints to application callables."""

    @property
    def hostname(self):
        """Current host name.

        :rtype: str

        """
        return decode(_uwsgi.hostname)

    @property
    def config(self):
        """The current configuration options, including any custom placeholders.

        :rtype: dict

        """
        return decode_deep(_uwsgi.opt)

    @property
    def config_variables(self):
        """Current mapping of configuration file "magic" variables.

        :rtype: dict

        """
        return decode_deep(_uwsgi.magic_table)

    @property
    def worker_id(self):
        """Returns current worker ID. 0 if not a worker (e.g. mule).

        :rtype: int
        """
        return _uwsgi.worker_id()

    @property
    def workers_info(self):
        """Gets statistics for all the workers for the current server.

        Returns tuple of dicts.

        :rtype: tuple[dict]
        """
        return tuple(decode_deep(item) for item in _uwsgi.workers())

    @property
    def ready_for_requests(self):
        """Returns flag indicating whether we are ready to handle requests.

        :rtype: bool
        """
        return _uwsgi.ready()

    @property
    def master_pid(self):
        """Return the process identifier (PID) of the uWSGI master process.

        :rtype: int
        """
        return _uwsgi.masterpid()

    @property
    def memory(self):
        """Returns memory usage tuple of ints: (rss, vsz).

        :rtype: tuple[int, int]
        """
        return _uwsgi.mem()

    @property
    def clock(self):
        """Returns uWSGI clock microseconds.

        :rtype: long
        """
        return _uwsgi.micros()

    def get_listen_queue(self, socket_num=0):
        """Returns listen queue (backlog size) of the given socket.

        :param int socket_num: Socket number.

        :rtype: int

        :raises ValueError: If socket is not found
        """
        return _uwsgi.listen_queue(socket_num)

    def get_version(self, as_tuple=False):
        """Returns uWSGI version string or tuple.

        :param bool as_tuple:

        :rtype: str|tuple
        """
        if as_tuple:
            return _uwsgi.version_info

        return decode(_uwsgi.version)


__THREAD_LOCAL = local()


def __get_platform():
    """
    :rtype: _Platform
    """
    platform = getattr(__THREAD_LOCAL, 'uwsgi_platform', None)

    if platform is None:
        platform = _Platform()
        platform.request = _Request()

        setattr(__THREAD_LOCAL, 'uwsgi_platform', platform)

    return platform


uwsgi = __get_platform()
"""This is a _Platform instance."""
