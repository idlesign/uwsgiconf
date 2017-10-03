from ..base import ParametrizedValue


class Logger(ParametrizedValue):

    args_joiner = ','

    def __init__(self, alias, *args):
        self.alias = alias or ''
        super(Logger, self).__init__(*args)


class LoggerFile(Logger):
    """Allows logging into files."""

    name = 'file'
    plugin = 'logfile'

    def __init__(self, filepath, alias=None):
        """
        :param str|unicode filepath: File path.

        :param str|unicode alias: Logger alias.

        """
        super(LoggerFile, self).__init__(alias, filepath)


class LoggerSocket(Logger):
    """Allows logging into UNIX and UDP sockets."""

    name = 'socket'
    plugin = 'logsocket'

    def __init__(self, addr_or_path, alias=None):
        """

        :param str|unicode addr_or_path: Remote address or filepath.

            Examples:
                * /tmp/uwsgi.logsock
                * 192.168.173.19:5050

        :param str|unicode alias: Logger alias.

        """
        super(LoggerSocket, self).__init__(alias, addr_or_path)


class LoggerSyslog(Logger):
    """Allows logging into Unix standard syslog."""

    name = 'syslog'
    plugin = 'syslog'

    def __init__(self, app_name=None, facility=None, alias=None):
        """

        :param str|unicode app_name:

        :param str|unicode facility:

            * https://en.wikipedia.org/wiki/Syslog#Facility

        :param str|unicode alias: Logger alias.

        """
        super(LoggerSyslog, self).__init__(alias, app_name, facility)


class LoggerRsyslog(LoggerSyslog):
    """Allows logging into Unix standard syslog or a remote syslog."""

    name = 'rsyslog'
    plugin = 'rsyslog'

    def __init__(self, app_name=None, host=None, facility=None, split=None, packet_size=None, alias=None):
        """

        :param str|unicode app_name:

        :param str|unicode host: Address (host and port) or UNIX socket path.

        :param str|unicode facility:

            * https://en.wikipedia.org/wiki/Syslog#Facility

        :param bool split: Split big messages into multiple chunks if they are bigger
            than allowed packet size. Default: ``False``.

        :param int packet_size: Set maximum packet size for syslog messages. Default: 1024.

            .. warning:: using packets > 1024 breaks RFC 3164 (#4.1)

        :param str|unicode alias: Logger alias.

        """
        super(LoggerRsyslog, self).__init__(app_name, facility, alias=alias)

        self.args.insert(0, host)

        self._set('rsyslog-packet-size', packet_size)
        self._set('rsyslog-split-messages', split, cast=bool)


class LoggerRedis(Logger):
    """Allows logging into Redis.

    .. note:: Consider using ``dedicate_thread`` param.

    """

    name = 'redislog'
    plugin = 'redislog'

    def __init__(self, host=None, command=None, prefix=None, alias=None):
        """

        :param str|unicode host: Default: 127.0.0.1:6379

        :param str|unicode command: Command to be used. Default: publish uwsgi

            Examples:
                * publish foobar
                * rpush foo

        :param str|unicode prefix: Default: <empty>

        :param str|unicode alias: Logger alias.

        """
        super(LoggerRedis, self).__init__(alias, host, command, prefix)


class LoggerMongo(Logger):
    """Allows logging into Mongo DB.

    .. note:: Consider using ``dedicate_thread`` param.

    """

    name = 'mongodblog'
    plugin = 'mongodblog'

    def __init__(self, host=None, collection=None, node=None, alias=None):
        """

        :param str|unicode host: Default: 127.0.0.1:27017

        :param str|unicode collection: Command to be used. Default: uwsgi.logs

        :param str|unicode node: An identification string for the instance
            sending logs Default: <server hostname>

        :param str|unicode alias: Logger alias.

        """
        super(LoggerMongo, self).__init__(alias, host, collection, node)


class LoggerZeroMq(Logger):
    """Allows logging into ZeroMQ sockets."""

    name = 'zeromq'
    plugin = 'logzmq'

    def __init__(self, connection_str, alias=None):
        """

        :param str|unicode connection_str:

            Examples:
                * tcp://192.168.173.18:9191

        :param str|unicode alias: Logger alias.

        """
        super(LoggerZeroMq, self).__init__(alias, connection_str)
