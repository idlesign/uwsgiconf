from ..base import OptionsGroup
from ..typehints import Strbool, Strlist
from ..utils import listify
from .logging_encoders import *
from .logging_loggers import *


class Var(TemplatedValue):

    def __str__(self):
        return '%(' + super().__str__() + ')'


class VarMetric(Var):

    tpl = 'metric.%s'


class VarRequestVar(Var):

    tpl = 'var.%s'

    def __init__(self, name):
        name = name.replace('-', '_').upper()  # Normalize.
        super().__init__(name)


class Logging(OptionsGroup):
    """Logging.

    * http://uwsgi.readthedocs.io/en/latest/Logging.html
    * http://uwsgi-docs.readthedocs.io/en/latest/LogFormat.html

    """

    class loggers:
        """Loggers available for ``add_logger()``."""

        file = LoggerFile
        fd = LoggerFileDescriptor
        stdio = LoggerStdIO
        mongo = LoggerMongo
        redis = LoggerRedis
        socket = LoggerSocket
        syslog = LoggerSyslog
        rsyslog = LoggerRsyslog
        zeromq = LoggerZeroMq

        # todo consider adding other loggers: crypto, graylog2, systemd

    class encoders:
        """Loggers available for ``add_logger_encoder()``."""

        compress = EncoderCompress
        format = EncoderFormat
        gzip = EncoderGzip
        json = EncoderJson
        newline = EncoderNewline
        prefix = EncoderPrefix
        suffix = EncoderSuffix

        # todo consider adding msgpack encoder

    def set_basic_params(
            self,
            *,
            no_requests: bool | None = None,
            template: str | None = None,
            memory_report: int | None = None,
            prefix: str | None = None,
            prefix_date: Strbool = None,
            apply_strftime: bool | None = None,
            response_ms: bool | None = None,
            ip_x_forwarded: bool | None = None
    ):
        """

        :param no_requests: Disable requests logging - only uWSGI internal messages
            and errors will be logged.

        :param template: Set advanced format for request logging.
            This template string can use variables from ``Logging.Vars``.

        :param prefix: Prefix log items with a string.

            .. note:: This will not work with `prefix_date` option.

        :param prefix_date: Prefix log items with date string.

            .. note:: This will not work with `prefix` option.
        
            .. note:: This can be ``True`` or contain formatting placeholders (e.g. %Y-%m-%d %H:%M:%S) 
               if used with ``apply_strftime``.

        :param memory_report: Enable memory report.
                * **1** - basic (default);
                * **2** - uss/pss (Linux only)

        :param apply_strftime: Apply strftime to dates in log entries.
            E.g. ``prefix_date`` can contain format placeholders. See also ``vars.REQ_START_FORMATTED``.

        :param response_ms: Report response time in microseconds instead of milliseconds.

        :param ip_x_forwarded: Use the IP from X-Forwarded-For header instead of REMOTE_ADDR.
            Used when uWSGI is run behind multiple proxies.

        """
        self._set('disable-logging', no_requests, cast=bool)
        self._set('log-format', template)
        self._set('memory-report', memory_report)
        self._set('log-prefix', prefix)

        if isinstance(prefix_date, str) and '%' in prefix_date:
            prefix_date = prefix_date.replace('%', '%%')  # Escaping.
                
        self._set('log-date', prefix_date, cast=(bool if isinstance(prefix_date, bool) else None))

        self._set('logformat-strftime', apply_strftime, cast=bool)
        self._set('log-micros', response_ms, cast=bool)
        self._set('log-x-forwarded-for', ip_x_forwarded, cast=bool)

        return self._section

    def log_into(self, target: str, *, before_priv_drop: bool = True):
        """Simple file or UDP logging.

        .. note:: This doesn't require any Logger plugin and can be used
            if no log routing is required.

        :param target: Filepath or UDP address.

        :param before_priv_drop: Whether to log data before or after privileges drop.

        """
        command = 'logto'

        if not before_priv_drop:
            command += '2'

        self._set(command, target)

        return self._section

    def set_file_params(
            self,
            *,
            reopen_on_reload: bool | None = None,
            truncate_on_startup: bool | None = None,
            max_size: int | None = None,
            rotation_fname: str | None = None,
            touch_reopen: Strlist = None,
            touch_rotate: Strlist = None,
            owner: str | None = None,
            mode: str | None = None
    ):
        """Set various parameters related to file logging.

        :param reopen_on_reload: Reopen log after reload.

        :param truncate_on_startup: Truncate log on startup.

        :param max_size: Set maximum logfile size in bytes after which log should be rotated.

        :param rotation_fname: Set log file name after rotation.

        :param touch_reopen: Trigger log reopen if the specified file
            is modified/touched.

            .. note:: This can be set to a file touched by ``postrotate`` script of ``logrotate``
                to implement rotation.

        :param touch_rotate: Trigger log rotation if the specified file
            is modified/touched.

        :param owner: Set owner chown() for logs.
        
        :param mode: Set mode chmod() for logs.

        """
        self._set('log-reopen', reopen_on_reload, cast=bool)
        self._set('log-truncate', truncate_on_startup, cast=bool)
        self._set('log-maxsize', max_size)
        self._set('log-backupname', rotation_fname)

        self._set('touch-logreopen', touch_reopen, multi=True)
        self._set('touch-logrotate', touch_rotate, multi=True)

        self._set('logfile-chown', owner)
        self._set('logfile-chmod', mode)

        return self._section

    def set_filters(
            self,
            *,
            include: Strlist = None,
            exclude: Strlist = None,
            write_errors: bool | None = None,
            write_errors_tolerance: int | None = None,
            sigpipe: bool | None = None
    ):
        """Set various log data filters.

        :param include: Show only log lines matching the specified regexp.

            .. note:: Requires enabled PCRE support.

        :param exclude: Do not show log lines matching the specified regexp.

            .. note:: Requires enabled PCRE support.

        :param write_errors: Log (annoying) write()/writev() errors. Default: ``True``.

            .. note:: If both this and ``sigpipe`` set to ``False``, it's the same
               as setting ``write-errors-exception-only`` uWSGI option.

        :param write_errors_tolerance: Set the maximum number of allowed write errors before exception
            is raised. Default: no tolerance.

            .. note:: Available for Python, Perl, PHP.

        :param sigpipe: Log (annoying) SIGPIPE. Default: ``True``.

            .. note:: If both this and ``write_errors`` set to ``False``, it's the same
               as setting ``write-errors-exception-only`` uWSGI option.

        """
        if write_errors is not None:
            self._set('ignore-write-errors', not write_errors, cast=bool)

        if sigpipe is not None:
            self._set('ignore-sigpipe', not sigpipe, cast=bool)

        self._set('write-errors-tolerance', write_errors_tolerance)

        for line in listify(include):
            self._set('log-filter', line, multi=True)

        for line in listify(exclude):
            self._set('log-drain', line, multi=True)

        return self._section

    def set_requests_filters(
            self,
            *,
            slower: int | None = None,
            bigger: int | None = None,
            status_4xx: bool | None = None,
            status_5xx: bool | None = None,
            no_body: bool | None = None,
            sendfile: bool | None = None,
            io_errors: bool | None = None
    ):
        """Set various log data filters.

        :param slower: Log requests slower than the specified number of milliseconds.

        :param bigger: Log requests bigger than the specified size in bytes.

        :param status_4xx: Log requests with a 4xx response.

        :param status_5xx: Log requests with a 5xx response.

        :param no_body: Log responses without body.

        :param sendfile: Log sendfile requests.

        :param io_errors: Log requests with io errors.

        """
        self._set('log-slow', slower)
        self._set('log-big', bigger)
        self._set('log-4xx', status_4xx, cast=bool)
        self._set('log-5xx', status_5xx, cast=bool)
        self._set('log-zero', no_body, cast=bool)
        self._set('log-sendfile', sendfile, cast=bool)
        self._set('log-ioerror', io_errors, cast=bool)

        return self._section

    def set_master_logging_params(
            self,
            *,
            enable: bool | None = None,
            dedicate_thread: bool | None = None,
            buffer: int | None = None,
            sock_stream: bool | None = None,
            sock_stream_requests_only: bool | None = None
    ):
        """Sets logging params for delegating logging to master process.

        :param enable: Delegate logging to master process.
            Delegate the write of the logs to the master process
            (this will put all of the logging I/O to a single process).
            Useful for system with advanced I/O schedulers/elevators.

        :param dedicate_thread: Delegate log writing to a thread.

            As error situations could cause the master to block while writing
            a log line to a remote server, it may be a good idea to use this option and delegate
            writes to a secondary thread.

        :param buffer: Set the buffer size for the master logger in bytes.
            Bigger log messages will be truncated.

        :param sock_stream: Create the master logpipe as SOCK_STREAM.

        :param sock_stream_requests_only: Create the master requests logpipe as SOCK_STREAM.

        """
        self._set('log-master', enable, cast=bool)
        self._set('threaded-logger', dedicate_thread, cast=bool)
        self._set('log-master-bufsize', buffer)

        self._set('log-master-stream', sock_stream, cast=bool)

        if sock_stream_requests_only:
            self._set('log-master-req-stream', sock_stream_requests_only, cast=bool)

        return self._section

    def print_loggers(self):
        """Print out available (built) loggers."""

        self._set('loggers-list', value=True, cast=bool)

        return self._section

    def add_logger(self, logger, *, requests_only: bool = False, for_single_worker: bool = False):
        """Set/add a common logger or a request requests only.

        :param str|list|Logger|list[Logger] logger:

        :param requests_only: Logger used only for requests information messages.

        :param for_single_worker: Logger to be used in single-worker setup.

        """
        if for_single_worker:
            command = 'worker-logger-req' if requests_only else 'worker-logger'
        else:
            command = 'logger-req' if requests_only else 'logger'

        for logger_ in listify(logger):
            self._set(command, logger_, multi=True)

        return self._section

    def add_logger_route(self, logger, matcher: str, *, requests_only: bool = False):
        """Log to the specified named logger if regexp applied on log item matches.

        :param str|list|Logger|list[Logger] logger: Logger to associate route with.

        :param matcher: Regular expression to apply to log item.

        :param requests_only: Matching should be used only for requests information messages.

        """
        command = 'log-req-route' if requests_only else 'log-route'

        for logger_ in listify(logger):
            self._set(command, f'{logger_} {matcher}', multi=True)

        return self._section

    def add_logger_encoder(self, encoder, *, logger=None, requests_only: bool = False, for_single_worker: bool = False):
        """Add an item in the log encoder or request encoder chain.

        * http://uwsgi-docs.readthedocs.io/en/latest/LogEncoders.html

            .. note:: Encoders automatically enable master log handling (see ``.set_master_logging_params()``).

            .. note:: For best performance consider allocating a thread
                for log sending with ``dedicate_thread``.

        :param str|list|Encoder encoder: Encoder (or a list) to add into processing.

        :param str|Logger logger: Logger apply associate encoders to.

        :param requests_only: Encoder to be used only for requests information messages.

        :param for_single_worker: Encoder to be used in single-worker setup.

        """
        if for_single_worker:
            command = 'worker-log-req-encoder' if requests_only else 'worker-log-encoder'
        else:
            command = 'log-req-encoder' if requests_only else 'log-encoder'

        for encoder_ in listify(encoder):

            value = f'{encoder_}'

            if logger:
                if isinstance(logger, Logger):
                    logger = logger.alias

                value += f':{logger}'

            self._set(command, value, multi=True)

        return self._section

    class vars:
        """Variables available for custom log formatting."""

        # The following are taken blindly from the internal wsgi_request structure of the current request.

        REQ_URI = '%(uri)'
        """REQUEST_URI from ``wsgi_request`` of the current request."""

        REQ_METHOD = '%(method)'
        """REQUEST_METHOD from ``wsgi_request`` of the current request."""

        REQ_REMOTE_USER = '%(user)'
        """REMOTE_USER from ``wsgi_request`` of the current request."""

        REQ_REMOTE_ADDR = '%(addr)'
        """REMOTE_ADDR from ``wsgi_request`` of the current request."""

        REQ_HTTP_HOST = '%(host)'
        """HTTP_HOST from ``wsgi_request`` of the current request."""

        REQ_SERVER_PROTOCOL = '%(proto)'
        """SERVER_PROTOCOL from ``wsgi_request`` of the current request."""

        REQ_USER_AGENT = '%(uagent)'
        """HTTP_USER_AGENT from ``wsgi_request`` of the current request."""

        REQ_REFERER = '%(referer)'
        """HTTP_REFERER from ``wsgi_request`` of the current request."""

        # The following are simple functions called to generate the logvar value.

        REQ_START_TS = '%(time)'
        """Timestamp of the start of the request. 
        E.g.: 1651848241"""

        REQ_START_CTIME = '%(ctime)'
        """Ctime of the start of the request. 
        E.g.: Fri May  6 21:44:01 2022"""

        REQ_START_UNIX_US = '%(tmsecs)'
        """Timestamp of the start of the request in milliseconds since the epoch.
        E.g.: 1651848241706

        .. note:: since 1.9.21

        """

        REQ_START_UNIX_MS = '%(tmicros)'
        """Timestamp of the start of the request in microseconds since the epoch.
        E.g.: 1651848241706778

        .. note:: since 1.9.21

        """

        REQ_START_HUMAN = '%(ltime)'
        """Human-formatted (Apache style) request time.
        E.g.: 06/May/2022:21:44:01 +0700"""

        REQ_START_FORMATTED = '%(ftime)'
        """Request time formatted with ``apply_strftime``. 

        .. note:: Use ``apply_strftime`` and placeholders.

        """

        REQ_SIZE_BODY = '%(cl)'
        """Request content body size."""

        REQ_COUNT_VARS_CGI = '%(vars)'
        """Number of CGI vars in the request."""

        REQ_COUNT_ERR_READ = '%(rerr)'
        """Number of read errors for the request.

        .. note:: since 1.9.21

        """

        REQ_COUNT_ERR_WRITE = '%(werr)'
        """Number of write errors for the request.

        .. note:: since 1.9.21

        """

        REQ_COUNT_ERR = '%(ioerr)'
        """Number of write and read errors for the request.

        .. note:: since 1.9.21

        """

        RESP_STATUS = '%(status)'
        """HTTP response status code."""

        RESP_TIME_US = '%(micros)'
        """Response time in microseconds. E.g.: 1512623650704"""

        RESP_TIME_MS = '%(msecs)'
        """Response time in milliseconds. E.g.: 1512623650704413"""

        RESP_SIZE = '%(size)'
        """Response body size + response headers size."""

        RESP_SIZE_HEADERS = '%(hsize)'
        """Response headers size."""

        RESP_SIZE_BODY = '%(rsize)'
        """Response body size."""

        RESP_COUNT_HEADERS = '%(headers)'
        """Number of generated response headers."""

        TIME_UNIX = '%(epoch)'
        """The current time in Unix format.
        E.g.: 1651848242"""

        WORKER_PID = '%(pid)'
        """pid of the worker handling the request."""

        WORKER_ID = '%(wid)'
        """id of the worker handling the request."""

        ASYNC_SWITCHES = '%(switches)'
        """Number of async switches."""

        CORE = '%(core)'
        """The core running the request."""

        MEM_VSZ = '%(vsz)'
        """Address space/virtual memory usage (in bytes)."""

        MEM_RSS = '%(rss)'
        """RSS memory usage (in bytes)."""

        MEM_VSZ_MB = '%(vszM)'
        """Address space/virtual memory usage (in megabytes)."""

        MEM_RSS_MV = '%(rssM)'
        """RSS memory usage (in megabytes)."""

        SIZE_PACKET_UWSGI = '%(pktsize)'
        """Size of the internal request uwsgi packet."""

        MOD1 = '%(modifier1)'
        """``modifier1`` of the request. See ``.routing.modifiers``."""

        MOD2 = '%(modifier2)'
        """``modifier2`` of the request. See ``.routing.modifiers``."""

        metric = VarMetric
        """Metric value (see The Metrics subsystem)."""

        request_var = VarRequestVar
        """Request variable value."""
