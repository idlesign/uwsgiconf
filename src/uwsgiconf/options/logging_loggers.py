from ..base import ParametrizedValue
from ..typehints import Strpath


class Logger(ParametrizedValue):

    args_joiner = ','

    def __init__(self, alias: str, *args):
        self.alias = alias or ''
        super().__init__(*args)


class LoggerFile(Logger):
    """Allows logging into files."""

    name = 'file'
    plugin = 'logfile'

    def __init__(self, filepath: Strpath, *, alias: str | None = None):
        """
        :param filepath: File path.

        :param alias: Logger alias.

        """
        super().__init__(alias, f'{filepath}')


class LoggerFileDescriptor(Logger):
    """Allows logging using file descriptor."""

    name = 'fd'
    plugin = 'logfile'

    def __init__(self, fd: int, *, alias: str | None = None):
        """
        :param fd: File descriptor.

        :param alias: Logger alias.

        """
        super().__init__(alias, fd)


class LoggerStdIO(Logger):
    """Allows logging stdio."""

    name = 'stdio'
    plugin = 'logfile'

    def __init__(self, *, alias: str | None = None):
        """

        :param alias: Logger alias.

        """
        super().__init__(alias)


class LoggerSocket(Logger):
    """Allows logging into UNIX and UDP sockets."""

    name = 'socket'
    plugin = 'logsocket'

    def __init__(self, addr_or_path: Strpath, *, alias: str | None = None):
        """

        :param addr_or_path: Remote address or filepath.

            Examples:
                * /tmp/uwsgi.logsock
                * 192.168.173.19:5050

        :param alias: Logger alias.

        """
        super().__init__(alias, f'{addr_or_path}')


class LoggerSyslog(Logger):
    """Allows logging into Unix standard syslog."""

    name = 'syslog'
    plugin = 'syslog'

    def __init__(self, *, app_name: str | None = None, facility: str | None = None, alias: str | None = None):
        """

        :param app_name:

        :param facility:

            * https://en.wikipedia.org/wiki/Syslog#Facility

        :param alias: Logger alias.

        """
        super().__init__(alias, app_name, facility)


class LoggerRsyslog(LoggerSyslog):
    """Allows logging into Unix standard syslog or a remote syslog."""

    name = 'rsyslog'
    plugin = 'rsyslog'

    def __init__(
            self,
            *,
            app_name: str | None = None,
            host: str | None = None,
            facility: str | None = None,
            split: bool | None = None,
            packet_size: int | None = None,
            alias: str | None = None
    ):
        """

        :param app_name:

        :param host: Address (host and port) or UNIX socket path.

        :param facility:

            * https://en.wikipedia.org/wiki/Syslog#Facility

        :param split: Split big messages into multiple chunks if they are bigger
            than allowed packet size. Default: ``False``.

        :param packet_size: Set maximum packet size for syslog messages. Default: 1024.

            .. warning:: using packets > 1024 breaks RFC 3164 (#4.1)

        :param alias: Logger alias.

        """
        super().__init__(app_name=app_name, facility=facility, alias=alias)

        self.args.insert(0, host)

        self._set('rsyslog-packet-size', packet_size)
        self._set('rsyslog-split-messages', split, cast=bool)


class LoggerRedis(Logger):
    """Allows logging into Redis.

    .. note:: Consider using ``dedicate_thread`` param.

    """

    name = 'redislog'
    plugin = 'redislog'

    def __init__(
            self,
            *,
            host: str | None = None,
            command: str | None = None,
            prefix: str | None = None,
            alias: str | None = None
    ):
        """

        :param host: Default: 127.0.0.1:6379

        :param command: Command to be used. Default: publish uwsgi

            Examples:
                * publish foobar
                * rpush foo

        :param prefix: Default: <empty>

        :param alias: Logger alias.

        """
        super().__init__(alias, host, command, prefix)


class LoggerMongo(Logger):
    """Allows logging into Mongo DB.

    .. note:: Consider using ``dedicate_thread`` param.

    """

    name = 'mongodblog'
    plugin = 'mongodblog'

    def __init__(
            self,
            *,
            host: str | None = None,
            collection: str | None = None,
            node: str | None = None,
            alias: str | None = None
    ):
        """

        :param host: Default: 127.0.0.1:27017

        :param collection: Command to be used. Default: uwsgi.logs

        :param node: An identification string for the instance
            sending logs Default: <server hostname>

        :param alias: Logger alias.

        """
        super().__init__(alias, host, collection, node)


class LoggerZeroMq(Logger):
    """Allows logging into ZeroMQ sockets."""

    name = 'zeromq'
    plugin = 'logzmq'

    def __init__(self, connection_str: str, *, alias: str | None = None):
        """

        :param connection_str:

            Examples:
                * tcp://192.168.173.18:9191

        :param alias: Logger alias.

        """
        super().__init__(alias, connection_str)
