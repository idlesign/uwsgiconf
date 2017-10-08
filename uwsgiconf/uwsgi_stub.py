
SPOOL_IGNORE = 0
"""Spooler function result.

Ignore this task, if multiple languages are loaded in the instance all 
of them will fight for managing the task. 
This return values allows you to skip a task in specific languages.

* http://uwsgi-docs.readthedocs.io/en/latest/Spooler.html#setting-the-spooler-function-callable

"""

SPOOL_OK = -2
"""Spooler function result.

The task has been completed, the spool file will be removed.

* http://uwsgi-docs.readthedocs.io/en/latest/Spooler.html#setting-the-spooler-function-callable

"""

SPOOL_RETRY = -1
"""Spooler function result.

Something is temporarily wrong, the task will be retried at the next spooler iteration.

* http://uwsgi-docs.readthedocs.io/en/latest/Spooler.html#setting-the-spooler-function-callable

"""

SymbolsImporter = None  # type: type
"""SymbolsImporter type."""

SymbolsZipImporter = None  # type: type
"""SymbolsZipImporter type."""

ZipImporter = None  # type: type
"""ZipImporter type."""

applications = None  # type: dict
"""Applications dictionary mapping mountpoints to application callables.

.. note:: Can be ``None``.

* http://uwsgi.readthedocs.io/en/latest/Python.html#application-dictionary

"""

buffer_size = None  # type: int
"""The current configured buffer size in bytes."""

cores = None  # type: int
"""Detected number of processor cores."""

env = None  # type: dict
"""Request environment dictionary."""

has_threads = None  # type: bool
"""Flag indicating whether thread support is enabled."""

hostname = None  # type: str
"""Current host name."""

magic_table = None  # type: dict
"""Current mapping of configuration file "magic" variables.

* http://uwsgi.readthedocs.io/en/latest/Configuration.html#magic-variables

"""

numproc = None  # type: int
"""Number of workers (processes) currently running."""

opt = None  # type: dict
"""The current configuration options, including any custom placeholders."""

started_on = 0  # type: int
"""uWSGI's startup Unix timestamp."""

start_response = None  # type: object
"""Callable spitting UWSGI response."""

unbit = None  # type: bool
"""Unbit internal flag."""

version = None  # type: bytes
"""The uWSGI version string.

.. warning:: Bytes are returned for Python 3.

:rtype: bytes|str
"""

version_info = None  # type: tuple
"""Five-elements version number tuple.

:rtype: tuple[int, int, int, int, bytes|str]
"""


def accepting():
    """Called to notify the master that the worker is accepting requests,
    this is required for ``touch_chain_reload`` to work.

    :rtype: None
    """


def add_cron(signal, minute, hour, day, month, weekday):
    """Adds cron. The interface to the uWSGI signal cron facility. The syntax is

    .. note:: The last 5 arguments work similarly to a standard crontab,
        but instead of "*", use -1, and instead of "/2", "/3", etc. use -2 and -3, etc.

    :param int signal: Signal to raise.

    :param int minute: Minute 0-59. Defaults to `each`.

    :param int hour: Hour 0-23. Defaults to `each`.

    :param int day: Day of the month number 1-31. Defaults to `each`.

    :param int month: Month number 1-12. Defaults to `each`.

    :param int weekday: Day of a the week number. Defaults to `each`.
        0 - Sunday  1 - Monday  2 - Tuesday  3 - Wednesday
        4 - Thursday  5 - Friday  6 - Saturday

    :rtype: bool

    :raises ValueError: If unable to add cron rule.
    """


def add_file_monitor(signal, filename):
    """Maps a specific file/directory modification event to a signal.

    :param int signal: Signal to raise.

    :param str|unicode filename: File or a directory to watch for its modification.

    :rtype: None

    :raises ValueError: If unable to register monitor.
    """


def add_ms_timer(signal, period):
    """Add a microsecond resolution timer.

    :param int signal: Signal to raise.

    :param int period: The interval (microseconds) at which to raise the signal.

    :rtype: None

    :raises ValueError: If unable to add timer.
    """


def add_rb_timer(signal, period, repeat=0):
    """Add a red-black timer.

    :param int signal: Signal to raise.

    :param int period: The interval (seconds) at which the signal is raised.

    :param int repeat: How many times to repeat. Default: 0 - infinitely.

    :rtype: None

    :raises ValueError: If unable to add timer.
    """


def add_timer(signal, period):
    """Add timer.

    :param int signal: Signal to raise.

    :param int period: The interval (seconds) at which to raise the signal.

    :rtype: None

    :raises ValueError: If unable to add timer.
    """


def add_var(name, value):
    """Registers custom request variable.

    Can be used for better integration with the internal routing subsystem.

    :param str|unicode name:

    :param str|unicode value:

    :rtype: bool

    :raises ValueError: If buffer size is not enough.
    """


def alarm(name, message):
    """Issues the given alarm with the given message.

    :param str|unicode name:

    :param str|unicode message: Message to pass to alarm.

    :rtype: None
    """


def async_connect(socket):
    """Issues socket connection. And returns a file descriptor.

    * http://uwsgi.readthedocs.io/en/latest/Async.html

    :param str|unicode socket:

    :rtype: int
    """


def async_sleep(seconds):
    """Suspends handling the current request and passes control to the next async core.

    * http://uwsgi.readthedocs.io/en/latest/Async.html

    :param seconds: Sleep time, in seconds.

    :rtype None:
    """


def cache_clear(cache):
    """Clears cache with the given name.

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: None
    """


def cache_dec(key, value=1, expires=None, cache=None):
    """Decrements the specified key value by the specified value.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.9.html#math-for-cache

    :param str|unicode key:

    :param int value:

    :param int expires: Expire timeout (seconds).

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bool
    """


def cache_del(key, cache=None):
    """Deletes the given cached key from the cache.

    :param str|unicode key: The cache key to delete.

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: None
    """


def cache_div(key, value=2, expires=None, cache=None):
    """Divides the specified key value by the specified value.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.9.html#math-for-cache

    :param str|unicode key:

    :param int value:

    :param int expires: Expire timeout (seconds).

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bool
    """


def cache_exists(key, cache=None):
    """Checks whether there is a value in the cache associated with the given key.

    :param str|unicode key: The cache key to check.

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bool
    """


def cache_get(key, cache=None):
    """Gets a value from the cache.

    .. warning:: Bytes are returned for Python 3.

    :param str|unicode key: The cache key to get value for.

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bytes|str
    """


def cache_inc(key, value=1, expires=None, cache=None):
    """Increments the specified key value by the specified value.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.9.html#math-for-cache

    :param str|unicode key:

    :param int value:

    :param int expires: Expire timeout (seconds).

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bool
    """


def cache_keys(cache=None):
    """Returns a list of keys available in cache.

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: list

    :raises ValueError: If cache is unavailable.
    """


def cache_mul(key, value=2, expires=None, cache=None):
    """Multiplies the specified key value by the specified value.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.9.html#math-for-cache

    :param str|unicode key:

    :param int value:

    :param int expires: Expire timeout (seconds).

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bool
    """


def cache_num(key, cache=None):
    """Gets the 64bit number from the specified item.

    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.9.html#math-for-cache

    :param str|unicode key: The cache key to get value for.

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: int|long
    """


def cache_set(key, value, expires=None, cache=None):
    """Sets the specified key value.

    :param str|unicode key:

    :param int value:

    :param int expires: Expire timeout (seconds).

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bool
    """


def cache_update(key, value, expires=None, cache=None):
    """Updates the specified key value.

    :param str|unicode key:

    :param int value:

    :param int expires: Expire timeout (seconds).

    :param str|unicode cache: Cache name with optional address (if @-syntax is used).

    :rtype: bool
    """


def call(func_name, *args):
    """Performs an [RPC] function call with the given arguments.

    .. warning:: Bytes are returned for Python 3.

    :param str|unicode func_name: Function name to call
        with optional address (if @-syntax is used).

    :param list[str|bytes] args:

    :rtype: bytes|str
    """


def chunked_read(timeout):
    """Reads chunked input.

    .. warning:: Bytes are returned for Python 3.

    * http://uwsgi.readthedocs.io/en/latest/Chunked.html
    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.13.html#chunked-input-api

    :param int timeout: Wait timeout (seconds).

    :rtype: bytes|str

    :raises IOError: If unable to receive chunked part.
    """


def chunked_read_nb():
    """Reads chunked input without blocking.

    .. warning:: Bytes are returned for Python 3.

    * http://uwsgi.readthedocs.io/en/latest/Chunked.html
    * http://uwsgi.readthedocs.io/en/latest/Changelog-1.9.13.html#chunked-input-api

    :rtype: bytes|str

    :raises IOError: If unable to receive chunked part.
    """


def cl():
    """Returns current post content length.

    :rtype: int|long
    """


def close(fd):
    """Closes the given file descriptor.

    :param int fd: File descriptor.

    :rtype: None
    """


def connect(socket, timeout=0):
    """Connects to the socket.

    :param str|unicode socket: Socket name.

    :param int timeout: Timeout (seconds).

    :rtype: int
    """


def connection_fd():
    """Returns current request file descriptor.

    :rtype: int
    """


def disconnect():
    """Drops current connection.

    :rtype: None
    """


def embedded_data(symbol_name):
    """Reads a symbol from the uWSGI binary image.

    * http://uwsgi.readthedocs.io/en/latest/Embed.html

    .. warning:: Bytes are returned for Python 3.

    :param str|unicode symbol_name: The symbol name to extract.

    :rtype: bytes|str

    :raises ValueError: If symbol is unavailable.
    """


def extract(fname):
    """Extracts file contents.

    .. warning:: Bytes are returned for Python 3.

    :param str|unicode fname:

    :rtype: bytes|str
    """


def farm_get_msg():
    """Reads a mule farm message.

     * http://uwsgi.readthedocs.io/en/latest/Embed.html

     .. warning:: Bytes are returned for Python 3.

     :rtype: bytes|str|None

     :raises ValueError: If not in a mule
     """


def farm_msg(farm, message):
    """Sends a message to the given farm.

    :param str|unicode farm: Farm name to send message to.

    :param str|unicode message:

    :rtype: None
    """


def get_logvar(name):
    """Return user-defined log variable contents.

    * http://uwsgi.readthedocs.io/en/latest/LogFormat.html#user-defined-logvars

    .. warning:: Bytes are returned for Python 3.

    :param str|unicode name:

    :rtype: bytes|str
    """


def green_schedule():
    """Switches to another green thread.

    .. note:: Alias for ``suspend``.

    * http://uwsgi.readthedocs.io/en/latest/Async.html#suspend-resume

    :type: bool
    """


def suspend():
    """Suspends handling of current coroutine/green thread and passes control
    to the next async core.

    * http://uwsgi.readthedocs.io/en/latest/Async.html#suspend-resume

    :type: bool
    """


def i_am_the_lord(legion_name):
    """Returns flag indicating whether you are the lord
    of the given legion.

    * http://uwsgi.readthedocs.io/en/latest/Legion.html#legion-api

    :param str|unicode legion_name:

    :rtype: bool
    """


def i_am_the_spooler():
    """Returns flag indicating whether you are the Spooler.

    :rtype: bool
    """


def in_farm(name):
    """Returns flag indicating whether you are (mule) belong
    to the given farm.

    :param str|unicode name: Farm name.

    :rtype: bool
    """


def is_a_reload():
    """Returns flag indicating whether reloading mechanics is used.

    :rtype: bool
    """


def is_connected(fd):
    """Checks the given file descriptor.

    :param int fd: File descriptor

    :rtype: bool
    """


def is_locked(lock_num=0):
    """Checks for the given lock.

    .. note:: Lock 0 is always available.

    :param int lock_num: Lock number.

    :rtype: bool

    :raises ValueError: For Spooler or invalid lock number
    """


def listen_queue(socket_num):
    """Returns listen queue (backlog size) of the given socket.

    :param int socket_num: Socket number.

    :rtype: bool

    :raises ValueError: If socket is not found
    """


def lock(lock_num=0):
    """Sets the given lock.

    .. note:: Lock 0 is always available.

    :param int lock_num: Lock number.

    :rtype: None

    :raises ValueError: For Spooler or invalid lock number
    """


def log(message):
    """Logs a message.

    :param str|unicode message:

    :rtype: bool
    """


def log_this_request():
    """Instructs uWSGI to log current request data.

    :rtype: None
    """


def logsize():
    """Returns current log size.

    :rtype|long
    """


def loop():
    """Returns current event loop name or None if loop is not set.

    :rtype: st|unicode|None
    """


def lord_scroll(legion_name):
    """Returns a Lord scroll for the Legion.

    * http://uwsgi.readthedocs.io/en/latest/Legion.html#lord-scroll-coming-soon

    :param str|unicode legion_name:

    :rtype: bool
    """


def masterpid():
    """Return the process identifier (PID) of the uWSGI master process.

    :rtype: int
    """


def mem():
    """Returns memory usage tuple of ints: (rss, vsz).

    :rtype: tuple
    """


def metric_dec(key, value=1):
    """Decrements the specified metric key value by the specified value.

    :param str|unicode key:

    :param int value:

    :rtype: bool
    """


def metric_div(key, value=1):
    """Divides the specified metric key value by the specified value.

    :param str|unicode key:

    :param int value:

    :rtype: bool
    """


def metric_inc(key, value=1):
    """Increments the specified metric key value by the specified value.

    :param str|unicode key:

    :param int value:

    :rtype: bool
    """


def metric_mul(key, value=1):
    """Multiplies the specified metric key value by the specified value.

    :param str|unicode key:

    :param int value:

    :rtype: bool
    """


def metric_get(key):
    """Returns metric value by key.

    :param str|unicode key:

    :rtype: int|long
    """


def metric_set(key, value):
    """Sets metric value.

    :param str|unicode key:

    :param int|long value:

    :rtype: bool
    """


def metric_set_max(key, value):
    """Sets metric value if it is greater that the current one.

    :param str|unicode key:

    :param int|long value:

    :rtype: bool
    """


def metric_set_min(key, value):
    """Sets metric value if it is less that the current one.

    :param str|unicode key:

    :param int|long value:

    :rtype: bool
    """


def micros():
    """Returns uWSGI clock microseconds.

    :rtype|long
    """


def mule_get_msg(signals=None, farms=None, buffer_size=65536, timeout=-1):
    """Block until a mule message is received and return it.

    This can be called from multiple threads in the same programmed mule.

    .. warning:: Bytes are returned for Python 3.

    :param bool signals: Whether to manage signals.

    :param bool farms: Whether to manage farms.

    :param int buffer_size:

    :param int timeout: Seconds.

    :rtype: bytes|str

    :raises ValueError: If not in a mule.
    """


def mule_id():
    """Returns current mule ID.

    :rtype: int
    """


def mule_msg(message, mule_farm=None):
    """Sends a message to a mule(s)/farm.

    :param str|unicode message:

    :param mule_farm: Mule ID, or farm name.

    :rtype: bool

    :raises ValueError: If no mules, or mule ID or farm name is not recognized.
    """


def offload(filename):
    """Offloads a file.

    .. warning:: Currently not implemented.

    :param filename:

    :rtype: bytes|str

    :raises ValueError: If unable to offload.
    """


def parsefile(fpath):
    """Parses the given file.

    Currently implemented only Spooler file parsing.

    :param str|unicode fpath:

    :rtype: None
    """


def ready():
    """Returns flag indicating whether we are ready to handle requests.

    :rtype: bool
    """


def ready_fd():
    """Returns flag indicating whether file description related to request is ready.

    :rtype: bool
    """


def recv(fd, maxsize=4096):
    """Reads data from the given file descriptor.

    .. warning:: Bytes are returned for Python 3.

    :param int fd:

    :param int maxsize: Chunk size (bytes).

    :rtype: bytes|str
    """


def register_rpc(name, func):
    """Registers RPC function.

    * http://uwsgi.readthedocs.io/en/latest/RPC.html

    :param str|unicode name:

    :param callable func:

    :rtype: bool

    :raises ValueError: If unable to register function
    """


def register_signal(number, target, func):
    """Registers a signal handler.

    :param int number: Signal number.

    :param str|unicode target:

        * ``workers``  - run the signal handler on all the workers
        * ``workerN`` - run the signal handler only on worker N
        * ``worker/worker0`` - run the signal handler on the first available worker
        * ``active-workers`` - run the signal handlers on all the active [non-cheaped] workers

        * ``mules`` - run the signal handler on all of the mules
        * ``muleN`` - run the signal handler on mule N
        * ``mule/mule0`` - run the signal handler on the first available mule

        * ``spooler`` - run the signal on the first available spooler
        * ``farmN/farm_XXX``  - run the signal handler in the mule farm N or named XXX

        * http://uwsgi.readthedocs.io/en/latest/Signals.html#signals-targets

    :param callable func:

    :rtype: None

    :raises ValueError: If unable to register
    """


def reload():
    """Gracefully reloads uWSGI.

    * http://uwsgi.readthedocs.io/en/latest/Management.html#reloading-the-server

    :rtype: bool
    """


def request_id():
    """Returns current request number (handled by worker on core).

    :rtype: int
    """


def route(name, args_str):
    """Registers a named route for internal routing subsystem.

    :param str name: Route name

    :param args_str: Comma-separated arguments string.

    :rtype: int
    """


def rpc(address, func_name, *args):
    """Performs an RPC function call with the given arguments.

    * http://uwsgi.readthedocs.io/en/latest/RPC.html

    .. warning:: Bytes are returned for Python 3.

    :param str|unicode address:

    :param str|unicode func_name: Function name to call.

    :param list[str|bytes] args:

    :rtype: bytes|str

    :raises ValueError: If unable to call RPC function.
    """


def rpc_list():
    """Returns registered RPC functions names.

    :rtype: tuple
    """


def scrolls(legion_name):
    """Returns a list of Legion scrolls defined on cluster.

    :param str|unicode legion_name:

    :rtype: list
    """


def send(fd_or_data, data=None):
    """Puts data into file descriptor.

    * One argument. Data to write into request file descriptor.
    * Two arguments. 1. File descriptor; 2. Data to write.

    :param df_or_data:

    :param data:

    :rtype: bool
    """


def sendfile(fd_or_name, chunk_size=0, start_pos=0, filesize=0):
    """Runs a sendfile.

    :param int|str|unicode fd_or_name: File path or descriptor number.

    :param int chunk_size: Not used.

    :param int start_pos:

    :param int filesize: Filesize. If ``0`` will be determined automatically.

    :rtype: bool|None
    """


def set_logvar(name, value):
    """Sets log variable.

    :param str|unicode name:

    :param str|unicode value:

    :rtype: None
    """


def set_user_harakiri(timeout=0):
    """Sets user level harakiri.

    :param int timeout: Seconds. ``0`` disable timer.

    :rtype: None
    """


def set_warning_message(message):
    """Sets a warning. This will be reported by pingers.

    :param str|unicode message:

    :rtype: bool
    """


def setprocname(name):
    """Sets current process name.

    :param str|unicode name:

    :rtype: bool
    """


def signal(num, remote=''):
    """Sends the signal to master or remote.

    :param num: Signal number.

    :param str|unicode remote: Remote address.

    :rtype: None

    :raises ValueError: If remote rejected the signal.

    :raises IOError: If unable to deliver to remote.
    """


def signal_received():
    """Get the number of the last signal received.

    Used in conjunction with ``signal_wait``.

    * http://uwsgi-docs.readthedocs.io/en/latest/Signals.html#signal-wait-and-signal-received

    :rtype: int
    """


def signal_registered(num):
    """Verifies the given signal has been registered.

    :param int num:

    :rtype: bool|None
    """


def signal_wait(num=None):
    """Waits for the given of any signal.

    Block the process/thread/async core until a signal is received. Use signal_received to get the number of
    the signal received. If a registered handler handles a signal, signal_wait will be interrupted and the actual
    handler will handle the signal.

    * http://uwsgi-docs.readthedocs.io/en/latest/Signals.html#signal-wait-and-signal-received

    :param int num:

    :rtype: str|unicode

    :raises SystemError: If something went wrong.
    """


def sockets():
    """Returns a current list file descriptors for registered sockets.

    :rtype: list[int]
    """


def stop():
    """Stops uWSGI.

    :rtype: bool|None
    """


def total_requests():
    """Returns the total number of requests managed so far by the pool of uWSGI workers.

    :rtype: int
    """


def unlock(lock_num=0):
    """Unlocks the given lock.

    .. note:: Lock 0 is always available.

    :param int lock_num: Lock number.

    :rtype: None

    :raises ValueError: For Spooler or invalid lock number
    """


def wait_fd_read(fd, timeout=None):
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


def wait_fd_write(fd, timeout=None):
    """Suspends handling of the current request until there is nothing more
    to be written on file descriptor.

    May be called several times to add more file descriptors to the set to be watched.

    * http://uwsgi-docs.readthedocs.io/en/latest/Async.html#waiting-for-i-o

    :param int fd: File descriptor number.

    :param int timeout: Timeout. Default:  infinite.

    :rtype: bytes|str

    :raises IOError: If unable to read.
    """


def websocket_handshake(security_key=None, origin=None, proto=None):
    """Waits for websocket handshake.

    :param str|unicode security_key: Websocket security key to use.

    :param str|unicode origin: Override ``Sec-WebSocket-Origin``.

    :param str|unicode proto: Override ``Sec-WebSocket-Protocol``.

    :rtype: None

    :raises IOError: If unable to complete handshake.
    """


def websocket_recv(request_context=None):
    """Receives data from websocket.

    :param request_context:

    :rtype: bytes|str

    :raises IOError: If unable to receive a message.
    """


def websocket_recv_nb(request_context=None):
    """Receives data from websocket (non-blocking variant).

    :param request_context:

    :rtype: bytes|str

    :raises IOError: If unable to receive a message.
    """


def websocket_send(message, request_context=None):
    """Sends a message to websocket.

    :param str message: data to send

    :param request_context:

    :raises IOError: If unable to send a message.
    """


def websocket_send_binary(message, request_context=None):
    """Sends binary message to websocket.

    :param str message: data to send

    :param request_context:

    :raises IOError: If unable to send a message.
    """


def worker_id():
    """Returns current worker ID.

    :rtype: int
    """


def workers():
    """Gets statistics for all the workers for the current server.

    Returns tuple of dicts.

    :rtype: tuple[dict]
    """
