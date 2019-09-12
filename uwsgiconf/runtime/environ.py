from threading import local

from .. import uwsgi
from .request import _Request
from ..utils import decode


class _Environment(object):

    # todo slots

    request = None  # type: _Request

    hostname = uwsgi.hostname  # type: str
    """Current host name."""

    workers_count = uwsgi.numproc  # type: int
    """Number of workers (processes) currently running."""

    cores_count = uwsgi.cores  # type: int
    """Detected number of processor cores."""

    buffer_size = uwsgi.buffer_size  # type: int
    """The current configured buffer size in bytes."""

    threads_enabled = uwsgi.has_threads  # type: bool
    """Flag indicating whether thread support is enabled."""

    started_on = uwsgi.started_on  # type: int
    """uWSGI's startup Unix timestamp."""

    config_variables = uwsgi.magic_table  # type: dict
    """Current mapping of configuration file "magic" variables."""

    config = uwsgi.opt  # type: dict
    """The current configuration options, including any custom placeholders."""

    apps_map = uwsgi.applications  # type: dict
    """Applications dictionary mapping mountpoints to application callables."""

    @property
    def worker_id(self):
        """Returns current worker ID.

        :rtype: int
        """
        return uwsgi.worker_id()

    @property
    def workers_info(self):
        """Gets statistics for all the workers for the current server.

        Returns tuple of dicts.

        :rtype: tuple[dict]
        """
        return uwsgi.workers()

    @property
    def ready_for_requests(self):
        """Returns flag indicating whether we are ready to handle requests.

        :rtype: bool
        """
        return uwsgi.ready()

    @property
    def master_pid(self):
        """Return the process identifier (PID) of the uWSGI master process.

        :rtype: int
        """
        return uwsgi.masterpid()

    @property
    def memory(self):
        """Returns memory usage tuple of ints: (rss, vsz).

        :rtype: tuple[int, int]
        """
        return uwsgi.mem()

    @property
    def clock(self):
        """Returns uWSGI clock microseconds.

        :rtype|long
        """
        return uwsgi.micros()

    def get_listen_queue(self, socket_num=0):
        """Returns listen queue (backlog size) of the given socket.

        :param int socket_num: Socket number.

        :rtype: int

        :raises ValueError: If socket is not found
        """
        return uwsgi.listen_queue(socket_num)

    def get_version(self, as_tuple=False):
        """Returns uWSGI version string or tuple.

        :param bool as_tuple:

        :rtype: str|tuple
        """
        if as_tuple:
            return uwsgi.version_info

        return decode(uwsgi.version)


__THREAD_LOCAL = local()


def __get_env():
    environ = getattr(__THREAD_LOCAL, 'uwsgi_env', None)

    if environ is None:
        environ = _Environment()
        environ.request = _Request()

        setattr(__THREAD_LOCAL, 'uwsgi_env', environ)

    return environ


uwsgi_env = __get_env()
