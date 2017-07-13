from ..base import OptionsGroup, ParametrizedValue
from ..utils import listify


class Logger(ParametrizedValue):

    args_joiner = ','

    def __init__(self, alias, *args):
        self.alias = alias or ''
        super(Logger, self).__init__(*args)


class LoggerFile(Logger):
    """Allows logging into files."""

    name = 'file'
    plugin = 'logfile'

    def __init__(self, alias, filepath):
        """
        :param str|unicode alias: Logger alias.

        :param str|unicode filepath: File path.

        """
        super(LoggerFile, self).__init__(alias, filepath)


class LoggerSocket(Logger):
    """Allows logging into UNIX and UDP sockets."""

    name = 'socket'
    plugin = 'logsocket'

    def __init__(self, alias, addr_or_path):
        """
        :param str|unicode alias: Logger alias.

        :param str|unicode addr_or_path: Remote address or filepath.

            Examples:
                * /tmp/uwsgi.logsock
                * 192.168.173.19:5050

        """
        super(LoggerSocket, self).__init__(alias, addr_or_path)


class LoggerSyslog(Logger):
    """Allows logging into Unix standard syslog or a remote syslog."""

    name = 'syslog'
    plugin = 'syslog'

    def __init__(self, alias, app_name=None, facility=None, host=None):
        """
        :param str|unicode alias: Logger alias.

        :param str|unicode app_name:

        :param str|unicode facility:

        :param str|unicode host: Host and port for remote syslog.

        """
        args = []

        if host:
            self.name = 'rsyslog'
            self.requires_plugin = 'rsyslog'
            args.append(host)

        args.extend([app_name, facility])

        super(LoggerSyslog, self).__init__(alias, *args)


class LoggerRedis(Logger):
    """Allows logging into Redis.

    .. note:: Consider using ``dedicate_thread`` param.

    """

    name = 'redislog'
    plugin = 'redislog'

    def __init__(self, alias, host=None, command=None, prefix=None):
        """
        :param str|unicode alias: Logger alias.

        :param str|unicode host: Default: 127.0.0.1:6379

        :param str|unicode command: Command to be used. Default: publish uwsgi

            Examples:
                * publish foobar
                * rpush foo

        :param str|unicode prefix: Default: <empty>

        """
        super(LoggerRedis, self).__init__(alias, host, command, prefix)


class LoggerMongo(Logger):
    """Allows logging into Mongo DB.

    .. note:: Consider using ``dedicate_thread`` param.

    """

    name = 'mongodblog'
    plugin = 'mongodblog'

    def __init__(self, alias, host=None, collection=None, node=None):
        """
        :param str|unicode alias: Logger alias.

        :param str|unicode host: Default: 127.0.0.1:27017

        :param str|unicode collection: Command to be used. Default: uwsgi.logs

        :param str|unicode node: An identification string for the instance
            sending logs Default: <server hostname>

        """
        super(LoggerMongo, self).__init__(alias, host, collection, node)


class LoggerZeroMq(Logger):
    """Allows logging into ZeroMQ sockets."""

    name = 'zeromq'
    plugin = 'logzmq'

    def __init__(self, alias, connection_str):
        """
        :param str|unicode alias: Logger alias.

        :param str|unicode connection_str:

            Examples:
                * tcp://192.168.173.18:9191

        """
        super(LoggerZeroMq, self).__init__(alias, connection_str)


class Encoder(ParametrizedValue):

    name_separator = ' '


class EncoderPrefix(Encoder):
    """Add a raw prefix to each log msg."""

    name = 'prefix'

    def __init__(self, value):
        """

        :param str|unicode value: Value to be used as affix

        """
        super(EncoderPrefix, self).__init__(value)


class EncoderSuffix(EncoderPrefix):
    """Add a raw suffix to each log msg"""

    name = 'suffix'


class EncoderNewline(Encoder):
    """Add a newline char to each log msg."""

    name = 'nl'


class EncoderGzip(Encoder):
    """Compress each msg with gzip (requires zlib)."""

    name = 'gzip'


class EncoderCompress(Encoder):
    """Compress each msg with zlib compress (requires zlib)."""

    name = 'compress'


class EncoderFormat(Encoder):
    """Apply the specified format to each log msg."""

    name = 'format'

    def __init__(self, template):
        """

        :param str|unicode template: Template string.
            Available variables are listed in ``FormatEncoder.Vars``.

        """
        super(EncoderFormat, self).__init__(template)

    class vars(object):
        """Variables available to use."""

        MESSAGE = '${msg}'
        """Raw log message (newline stripped)."""

        MESSAGE_NEWLINE = '${msgnl}'
        """Raw log message (with newline)."""

        TIME = '${unix}'
        """Current unix time."""

        TIME_MS = '${micros}'
        """Current unix time in microseconds."""

        # todo consider adding ${strftime:xxx} - strftime using the xxx format


class EncoderJson(EncoderFormat):
    """Apply the specified format to each log msg with each variable json escaped."""

    name = 'json'


class Logging(OptionsGroup):
    """Logging.

    * http://uwsgi.readthedocs.io/en/latest/Locks.html
    * http://uwsgi-docs.readthedocs.io/en/latest/LogFormat.html

    """

    class loggers(object):
        """Loggers available for ``add_logger()``."""

        file = LoggerFile
        socket = LoggerSocket
        syslog = LoggerSyslog
        redis = LoggerRedis
        mongo = LoggerMongo
        zeromq = LoggerZeroMq
        # todo consider adding other loggers: crypto, graylog2, systemd

    class encoders(object):
        """Loggers available for ``add_logger_encoder()``."""

        prefix = EncoderPrefix
        suffix = EncoderSuffix
        newline = EncoderNewline
        gzip = EncoderGzip
        compress = EncoderCompress
        format = EncoderFormat
        json = EncoderJson
        # todo consider adding msgpack encoder

    def set_basic_params(
            self, no_requests=None, template=None, memory_report=None, prefix=None, prefix_date=None,
            apply_strftime=None, response_ms=None, ip_x_forwarded=None):
        """

        :param bool no_requests: Disable requests logging - only uWSGI internal messages
            and errors will be logged.

        :param str|unicode template: Set advanced format for request logging.
            This template string can use variables from ``Logging.Vars``.

        :param str|unicode prefix: Prefix log items with a string.

        :param str|unicode prefix_date: Prefix log items with date.

        :param int memory_report: Enable memory report.
                * **1** - basic (default);
                * **2** - uss/pss (Linux only)

        :param bool apply_strftime: Apply strftime to logformat output.

        :param bool response_ms: Report response time in microseconds instead of milliseconds.

        :param bool ip_x_forwarded: Use the IP from X-Forwarded-For header instead of REMOTE_ADDR.
            Used when uWSGI is run behind multiple proxies.

        """
        self._set('disable-logging', no_requests, cast=bool)
        self._set('log-format', template)
        self._set('memory-report', memory_report)
        self._set('log-prefix', prefix)
        self._set('log-date', prefix_date, cast=bool)
        self._set('logformat-strftime', apply_strftime, cast=bool)
        self._set('log-micros', response_ms, cast=bool)
        self._set('log-x-forwarded-for', ip_x_forwarded, cast=bool)

        return self._section

    def set_file_params(
            self, reopen_on_reload=None, trucate_on_statup=None, max_size=None, rotation_fname=None,
            touch_reopen=None, touch_rotate=None, owner=None, mode=None):
        """

        :param bool reopen_on_reload: Reopen log after reload.

        :param bool trucate_on_statup: Truncate log on startup.

        :param int max_size: Set maximum logfile size in bytes.

        :param str|unicode rotation_fname: Set log file name after rotation.

        :param str|unicode|list touch_reopen: Trigger log reopen if the specified file
            is modified/touched.

        :param str|unicode|list touch_rotate: Trigger log rotation if the specified file
            is modified/touched.

        :param str|unicode owner: Set owner chown() for logs.
        .
        :param str|unicode mode: Set mode chmod() for logs.

        """
        self._set('log-reopen', reopen_on_reload, cast=bool)
        self._set('log-truncate', trucate_on_statup, cast=bool)
        self._set('log-maxsize', max_size)
        self._set('log-backupname', rotation_fname)

        self._set('touch-logreopen', touch_reopen, multi=True)
        self._set('touch-logrotate', touch_rotate, multi=True)

        self._set('logfile-chown', owner)
        self._set('logfile-chmod', mode)

        return self._section

    def set_filters(
            self, include=None, exclude=None, slower=None, bigger=None, status_4xx=None, status_5xx=None,
            no_body=None, sendfile=None, io_errors=None):
        """

        :param str|unicode|list include: Show only log lines matching the specified regexp.

        :param str|unicode|list exclude: Do not show log lines matching the specified regexp.

        :param int slower: Log requests slower than the specified number of milliseconds.

        :param int bigger: Log requestes bigger than the specified size in bytes.

        :param status_4xx: Log requests with a 4xx response.

        :param status_5xx: Log requests with a 5xx response.

        :param bool no_body: Log responses without body.

        :param bool sendfile: Log sendfile requests.

        :param bool io_errors: Log requests with io errors.

        """
        self._set('log-slow', slower)
        self._set('log-big', bigger)
        self._set('log-4xx', status_4xx, cast=bool)
        self._set('log-5xx', status_5xx, cast=bool)
        self._set('log-zero', no_body, cast=bool)
        self._set('log-sendfile', sendfile, cast=bool)
        self._set('log-ioerror', io_errors, cast=bool)

        for line in listify(include):
            self._set('log-filter', line, multi=True)

        for line in listify(exclude):
            self._set('log-drain', line, multi=True)

        return self._section

    def set_master_logging_params(
            self, enable=None, dedicate_thread=None, buffer=None,
            sock_stream=None, sock_stream_requests_only=None):
        """Sets logging params for delegating logging to master process.

        :param bool enable: Delegate logging to master process.
            Delegate the write of the logs to the master process
            (this will put all of the logging I/O to a single process).
            Useful for system with advanced I/O schedulers/elevators.

        :param bool dedicate_thread: Delegate log writing to a thread.

            As error situations could cause the master to block while writing
            a log line to a remote server, it may be a good idea to use this option and delegate
            writes to a secondary thread.

        :param int buffer: Set the buffer size for the master logger in bytes.
            Bigger log messages will be truncated.

        :param bool|tuple sock_stream: Create the master logpipe as SOCK_STREAM.

        :param bool|tuple sock_stream_requests_only: Create the master requests logpipe as SOCK_STREAM.

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

        self._set('loggers-list', True, cast=bool)

        return self._section

    def add_logger(self, logger, requests_only=False, for_single_worker=False):
        """Set/add a common logger or a request requests only.

        :param str|unicode|list|Logger|list[Logger] logger:

        :param bool requests_only: Logger used only for requests information messages.

        :param bool for_single_worker: Logger to be used in single-worker setup.


        """
        if for_single_worker:
            command = 'worker-logger-req' if requests_only else 'worker-logger'
        else:
            command = 'req-logger' if requests_only else 'logger'

        for logger in listify(logger):
            self._set(command, logger, multi=True)

        return self._section

    def add_logger_route(self, logger, matcher, requests_only=False):
        """Log to the specified named logger if regexp applied on log item matches.

        :param str|unicode|list|Logger|list[Logger] logger: Logger to associate route with.

        :param str|unicode matcher: Regular expression to apply to log item.

        :param bool requests_only: Matching should be used only for requests information messages.

        """
        command = 'log-req-route' if requests_only else 'log-route'

        for logger in listify(logger):
            self._set(command, '%s %s' % (logger, matcher), multi=True)

        return self._section

    def add_logger_encoder(self, encoder, logger=None, requests_only=False, for_single_worker=False):
        """Add an item in the log encoder or request encoder chain.

        * http://uwsgi-docs.readthedocs.io/en/latest/LogEncoders.html

            .. note:: Encoders automatically enable master log handling (see ``.set_master_logging_params()``).

            .. note:: For best performance consider allocating a thread
                for log sending with ``dedicate_thread``.

        :param str|unicode|list|Encoder encoder: Encoder (or a list) to add into processing.

        :param str|unicode|Logger logger: Logger apply associate encoders to.

        :param bool requests_only: Encoder to be used only for requests information messages.

        :param bool for_single_worker: Encoder to be used in single-worker setup.

        """
        if for_single_worker:
            command = 'worker-log-req-encoder' if requests_only else 'worker-log-encoder'
        else:
            command = 'log-req-encoder' if requests_only else 'log-encoder'

        for encoder in listify(encoder):

            value = '%s' % encoder

            if logger:
                if isinstance(logger, Logger):
                    logger = logger.alias

                value += ':%s' % logger

            self._set(command, value, multi=True)

        return self._section

    class vars(object):
        """Variables available for custom log formatting."""

        # The following are taken blindly from the internal wsgi_request structure of the current request.

        REQ_URL = '%(uri)'
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

        # The following are simple functions called for generating the logvar value.

        RESP_STATUS = '%(status)'
        """HTTP response status code."""

        RESP_TIME_US = '%(micros)'
        """Response time in microseconds."""

        RESP_TIME_MS = '%(msecs)'
        """Response time in milliseconds."""

        REQ_START_TS = '%(time)'
        """Timestamp of the start of the request."""

        RESP_START_CTIME = '%(ctime)'
        """Ctime of the start of the request."""

        TIME_UNIX = '%(epoch)'
        """The current time in Unix format."""

        RESP_SIZE = '%(size)'
        """Response body size + response headers size."""

        REQ_TIME_HUMAN = '%(ltime)'
        """Human-formatted (Apache style) request time."""

        REQ_TIME_FORMATTED = '%(ftime)'
        """Request time formatted with ``date_format``."""

        RESP_SIZE_HEADER = '%(hsize)'
        """Response headers size."""

        RESP_SIZE_BODY = '%(rsize)'
        """Response body size."""

        REQ_SIZE_BODY = '%(cl)'
        """Request content body size."""

        WORKER_PID = '%(pid)'
        """pid of the worker handling the request."""

        WORKER_ID = '%(wid)'
        """id of the worker handling the request."""

        ASYNC_SWITCHES = '%(switches)'
        """Number of async switches."""

        REQ_COUNT_VARS_CGI = '%(vars)'
        """Number of CGI vars in the request."""

        RESP_COUNT_HEADERS = '%(headers)'
        """Number of generated response headers."""

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
        """modifier1 of the request."""

        MOD2 = '%(modifier2)'
        """modifier2 of the request."""

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

        REQ_START_UNIX_US = '%(tmsecs)'
        """Timestamp of the start of the request in milliseconds since the epoch.
    
        .. note:: since 1.9.21
    
        """

        REQ_START_UNIX_MS = '%(tmicros)'
        """Timestamp of the start of the request in microseconds since the epoch.
    
        .. note:: since 1.9.21
    
        """

        # todo %(metric.XXX) - access the XXX metric value (see The Metrics subsystem)
        # todo %(var.XXX)
