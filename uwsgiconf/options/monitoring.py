from .alarms import AlarmType
from ..base import OptionsGroup, ParametrizedValue
from ..utils import make_key_val_string, listify, filter_locals
from ..exceptions import ConfigurationError


class Metric(ParametrizedValue):

    type_str = None
    type_id = None
    name_separator = ','

    def __init__(
            self, name, oid=None, alias_for=None, collector=None,
            initial_value=None, collect_interval=None, reset_after_push=None):
        """

        :param str|unicode name: Metric name.

            .. note:: Only numbers, letters, underscores, dashes and dots.

        :param str|unicode alias_for: If set metric will be a simple alias for the specified one.

        :param str|unicode oid: Metric OID.

            Required for SNMP.

            * http://uwsgi-docs.readthedocs.io/en/latest/Metrics.html#oid-assigment-for-plugins

        :param Collector collector:

        :param int initial_value: Set the metric to a specific value on startup.

        :param int collect_interval:

        :param bool reset_after_push: Reset the metric to zero (or the configured initial_value)
            after it's been pushed.

        """
        self.name = name

        if alias_for:
            # Set any type to ``alias``.
            self.type_str = MetricTypeAlias.type_str
            self.type_id = MetricTypeAlias.type_id

            if isinstance(alias_for, Metric):
                alias_for = alias_for.name

        if self.type_id == MetricTypeAlias.type_id and not alias_for:
            raise ConfigurationError('Parameter ``alias_for`` is required for ``MetricTypeAlias``.')

        type_str = self.type_str

        value = make_key_val_string(
            filter_locals(locals(), drop=['name']),
            aliases={'collect_interval': 'freq', 'type_str': 'type', 'alias_for': 'alias'}
        )

        super(Metric, self).__init__(value)

    def __str__(self):
        return 'name=%s' % super(Metric, self).__str__()


class MetricTypeCounter(Metric):
    """A generally-growing up number.

        Example:
            * number of requests

    """
    type_str = 'counter'
    type_id = 0


class MetricTypeGauge(Metric):
    """A number that can increase or decrease dynamically.

        Example:
            * memory used by a worker
            * CPU load

    """
    type_str = 'gauge'
    type_id = 1


class MetricTypeAbsolute(Metric):
    """An absolute number.

        Example:
            * memory of the whole server
            * size of the hard disk.

    """
    type_str = 'absolute'
    type_id = 2


class MetricTypeAlias(Metric):
    """This is a virtual metric pointing to another one .

    You can use it to give different names to already existing metrics.

    """
    type_str = 'alias'
    type_id = 3


class Pusher(ParametrizedValue):

    args_joiner = ','


class PusherSocket(Pusher):
    """Push metrics to a UDP server.

    Uses the following format: ``<metric> <type> <value>``
    ``<type>`` - is in the numeric form of metric type.

    """
    name = 'socket'
    plugin = 'stats_pusher_socket'

    def __init__(self, address, prefix=None):
        """
        :param str|unicode address:

        :param str|unicode prefix: Arbitrary prefix to differentiate sender.
        """
        super(PusherSocket, self).__init__(address, prefix)


class PusherRrdtool(Pusher):
    """This will store an rrd file for each metric in the specified directory.

    Each rrd file has a single data source named "metric".

    """
    name = 'rrdtool'
    plugin = 'rrdtool'

    def __init__(self, target_dir):
        """
        :param str|unicode target_dir: Directory to store rrd files into.
        """
        super(PusherRrdtool, self).__init__(target_dir)

    def set_basic_params(self, library=None, push_interval=None):
        """
        :param str|unicode library: Set the name of rrd library. Default: librrd.so.

        :param int push_interval: Set push frequency.
        """
        self._set('rrdtool-freq', push_interval)
        self._set('rrdtool-lib', library)

        return self


class PusherStatsd(Pusher):
    """Push metrics to a statsd server."""

    name = 'statsd'
    plugin = 'stats_pusher_statsd'

    def __init__(self, address, prefix=None):
        """
        :param str|unicode address:

        :param str|unicode prefix: Arbitrary prefix to differentiate sender.
        """
        super(PusherStatsd, self).__init__(address, prefix)

    def set_basic_params(self, no_workers=None, all_gauges=None):
        """
        :param bool no_workers: Disable generation of single worker metrics.

        :param bool all_gauges: Push all metrics to statsd as gauges.
        """
        self._set('statsd-no-workers', no_workers, cast=bool)
        self._set('statsd-all-gauges', all_gauges, cast=bool)

        return self


class PusherCarbon(Pusher):
    """Push metrics to a Carbon server.

    * http://uwsgi.readthedocs.io/en/latest/Carbon.html
    * http://uwsgi.readthedocs.io/en/latest/tutorials/GraphiteAndMetrics.html

    """
    name = 'carbon'
    plugin = 'carbon'

    def __init__(self, address):
        """
        :param str|unicode address:
        """
        super(PusherCarbon, self).__init__(address)

    def set_basic_params(
            self, id=None, root_node=None, push_interval=None, idle_avg_source=None,
            use_metrics=None, no_workers=None):
        """

        :param str|unicode id: Set carbon id.

        :param str|unicode root_node: Set carbon metrics root node. Default: uwsgi.

        :param int push_interval: Set carbon push frequency in seconds. Default: 60.

        :param bool no_workers: Disable generation of single worker metrics.

        :param str|unicode idle_avg_source: Average values source during idle period (no requests).
            Default: last.

            Variants:
                * last
                * zero
                * none

        :param bool use_metrics: Don't compute all statistics, use metrics subsystem data
            instead.

            .. warning:: Key names will be different.

        """
        self._set('carbon-id', id)
        self._set('carbon-root', root_node)
        self._set('carbon-freq', push_interval)
        self._set('carbon-idle-avg', idle_avg_source)
        self._set('carbon-use-metrics', use_metrics, cast=bool)
        self._set('carbon-no-workers', no_workers, cast=bool)

        return self

    def set_connection_params(
            self, timeout=None, retries=None, retries_delay=None,
            hostname_dots_replacer=None, hostname_as_address=None):
        """Sets connection related parameters.

        :param int timeout: Set carbon connection timeout in seconds. Default: 3.

        :param int retries: Set maximum number of retries in case of connection errors. Default: 1.

        :param int retries_delay: Set connection retry delay in seconds. Default: 7.

        :param str|unicode hostname_dots_replacer: Set char to use as a replacement for
            dots in hostname (dots are not replaced by default).

        :param bool hostname_as_address: Allow using hostname as carbon server address. Default: disabled.

        """
        self._set('carbon-timeout', timeout)
        self._set('carbon-max-retry', retries)
        self._set('carbon-retry-delay', retries_delay)
        self._set('carbon-hostname-dots', hostname_dots_replacer)
        self._set('carbon-name-resolve', hostname_as_address, cast=bool)

        return self


class PusherZabbix(Pusher):
    """Push metrics to a zabbix server."""

    name = 'zabbix'
    plugin = 'zabbix'

    def __init__(self, address, prefix=None):
        """
        :param str|unicode address:

        :param str|unicode prefix: Arbitrary prefix to differentiate sender.
        """
        super(PusherZabbix, self).__init__(address, prefix)

    def set_basic_params(self, template=None):
        """
        :param str|unicode template: Print (or store to a file) the zabbix template
            for the current metrics setup.
        """
        self._set('zabbix-template', template)

        return self


class PusherMongo(Pusher):
    """Push statistics (as JSON) the the specified MongoDB database."""

    name = 'mongodb'
    plugin = 'stats_pusher_mongodb'

    def __init__(self, address=None, collection=None, push_interval=None):
        """
        :param str|unicode address: Default: 127.0.0.1:27017

        :param str|unicode collection: MongoDB colection to write into. Default: uwsgi.statistics

        :param int push_interval: Write interval in seconds.
        """
        value = make_key_val_string(locals(), aliases={'push_interval': 'freq'})

        super(PusherMongo, self).__init__(value)


class PusherFile(Pusher):
    """Stores stats JSON into a file.

    .. note:: Mainly for demonstration purposes.

    """
    name = 'file'
    plugin = 'stats_pusher_file'

    def __init__(self, fpath=None, separator=None, push_interval=None):
        """
        :param str|unicode fpath: File path. Default: uwsgi.stats

        :param str|unicode separator: New entry separator. Default: \n\n

        :param int push_interval: Write interval in seconds.
        """
        value = make_key_val_string(locals(), aliases={'fpath': 'path', 'push_interval': 'freq'})

        super(PusherFile, self).__init__(value)


class Collector(ParametrizedValue):

    name_separator = ','
    name_separator_strip = True
    args_joiner = ','

    def __init__(self, *args, **kwargs):
        args = list(args)

        # Adding children for metric to use.
        children = kwargs.pop('children', None)

        if children:
            children_ = []

            for child in children:
                if isinstance(child, Metric):
                    child = child.name
                children_.append(child)

            args.append('children=%s' % ';'.join(children_))

        super(Collector, self).__init__(*args)


class CollectorManual(Collector):
    """The value must be updated manually from applications using the metrics API."""

    name = 'manual'


class CollectorPointer(Collector):
    """The value is collected from memory pointer."""

    name = 'ptr'


class CollectorFile(Collector):
    """The value is collected from a file."""

    name = 'file'

    def __init__(self, fpath, get_slot=None):
        """
        :param str|unicode fpath: File path.

        :param int get_slot: Get value from the given slot number.
            Slots: the content is split (using \n, \t, spaces, \r and zero as separator)
            and the item (the returned array is zero-based) used as the return value.

        """
        value = make_key_val_string(locals(), aliases={'fpath': 'arg1', 'get_slot': 'arg1n'})

        super(CollectorFile, self).__init__(value)


class CollectorFunction(Collector):
    """The value is computed calling a specific C function every time.

    .. note::
        * The argument it takes is a ``uwsgi_metric`` pointer.
          You generally do not need to parse the metric, so just casting to void will avoid headaches.

        * The function must returns an ``int64_t`` value.

    """

    name = 'func'

    def __init__(self, func):
        """
        :param str|unicode func: Function to call.
        """
        value = make_key_val_string(locals(), aliases={'func': 'arg1'})

        super(CollectorFunction, self).__init__(value)


class CollectorSum(Collector):
    """The value is the sum of other metrics."""

    name = 'sum'

    def __init__(self, what):
        super(CollectorSum, self).__init__(children=what)


class CollectorAvg(Collector):
    """The value is the algebraic average of the children.

    .. note:: Since 1.9.20

    """
    name = 'avg'

    def __init__(self, what):
        super(CollectorAvg, self).__init__(children=what)


class CollectorAccumulator(Collector):
    """Always add the sum of children to the final value.

    Example:

        * Round 1: child1 = 22, child2 = 17 -> metric_value = 39
        * Round 2: child1 = 26, child2 = 30 -> metric_value += 56

    """
    name = 'accumulator'

    def __init__(self, what):
        super(CollectorAccumulator, self).__init__(children=what)


class CollectorAdder(Collector):
    """Add the specified argument (arg1n) to the sum of children.

    """
    name = 'adder'

    def __init__(self, what, value):
        """
        :param int value: Value to add (multiply if it is CollectorMultiplier).
        """
        value = make_key_val_string(filter_locals(locals(), drop=['what']), aliases={'value': 'arg1n'})

        super(CollectorAdder, self).__init__(value, children=what)


class CollectorMultiplier(CollectorAdder):
    """Multiply the sum of children by the specified argument.

    Example:

        * child1 = 22, child2 = 17, arg1n = 3 -> metric_value = (22+17)*3

    """
    name = 'multiplier'


class Monitoring(OptionsGroup):
    """Monitoring facilities.

    * SNMP - http://uwsgi.readthedocs.io/en/latest/SNMP.html
    * Stats - http://uwsgi.readthedocs.io/en/latest/StatsServer.html
    * Metrics - http://uwsgi.readthedocs.io/en/latest/Metrics.html

    """

    class metric_types(object):
        """Various metric types to represent data of various nature.

        User metrics must inherit from one of those.

        """
        counter = MetricTypeCounter
        gauge = MetricTypeGauge
        absolute = MetricTypeAbsolute
        alias = MetricTypeAlias

    class collectors(object):
        """Metric collection and accumulation means."""

        manual = CollectorManual
        pointer = CollectorPointer
        file = CollectorFile
        function = CollectorFunction
        sum = CollectorSum
        avg = CollectorAvg
        accumulator = CollectorAccumulator
        adder = CollectorAdder
        multiplier = CollectorMultiplier

    class pushers(object):
        """Means to deliver metrics to various remotes or locals.

        These are available for ``.register_stats_pusher()``.

        """
        socket = PusherSocket
        rrdtool = PusherRrdtool
        statsd = PusherStatsd
        carbon = PusherCarbon
        zabbix = PusherZabbix
        mongo = PusherMongo
        file = PusherFile

    def register_metric(self, metric):
        """

        Officially Registered Metrics:

            * ``worker`` 3 - exports information about workers.
                Example: worker.1.requests **[or 3.1.1]** reports the number of requests served by worker 1.

            * ``plugin`` 4  - namespace for metrics automatically added by plugins.
                Example: plugins.foo.bar

            * ``core`` 5  - namespace for general instance information.

            * ``router`` 6 - namespace for corerouters.
                Example: router.http.active_sessions

            * ``socket`` 7 - namespace for sockets.
                Example: socket.0.listen_queue

            * ``mule`` 8 - namespace for mules.
                Example:  mule.1.signals

            * ``spooler`` 9 - namespace for spoolers.
                Example: spooler.1.signals

            * ``system`` 10 - namespace for system metrics, like loadavg or free memory.

        :param Metric|list[Metric] metric: Metric object.

        """
        for metric in listify(metric):
            self._set('metric', metric, multi=True)

        return self._section

    def set_metrics_params(self, enable=None, store_dir=None, restore=None, no_cores=None):
        """Sets basic Metrics subsystem params.

        uWSGI metrics subsystem allows you to manage "numbers" from your apps.

        When enabled, the subsystem configures a vast amount of metrics
        (like requests per-core, memory usage, etc) but, in addition to this,
        you can configure your own metrics, such as the number of active users or, say,
        hits of a particular URL, as well as the memory consumption of your app or the whole server.

        * http://uwsgi.readthedocs.io/en/latest/Metrics.html
        * SNMP Integration - http://uwsgi.readthedocs.io/en/latest/Metrics.html#snmp-integration

        :param bool enable: Enables the subsystem.

        :param str|unicode store_dir: Directory to store metrics.
            The metrics subsystem can expose all of its metrics in the form
            of text files in a directory. The content of each file is the value
            of the metric (updated in real time).

        :param bool restore: Restore previous metrics from ``store_dir``.
            When you restart a uWSGI instance, all of its metrics are reset.
            Use the option to force the metric subsystem to read-back the values
            from the metric directory before starting to collect values.

        :param bool no_cores: Disable generation of cores-related metrics.

        """
        self._set('enable-metrics', enable, cast=bool)
        self._set('metrics-dir', store_dir)
        self._set('metrics-dir-restore', restore, cast=bool)
        self._set('metrics-no-cores', no_cores, cast=bool)

        return self._section

    def set_metrics_threshold(self, name, value, check_interval=None, reset_to=None, alarm=None, alarm_message=None):
        """Sets metric threshold parameters.

        :param str|unicode name: Metric name.

        :param int value: Threshold value.

        :param int reset_to: Reset value to when threshold is reached.

        :param int check_interval: Threshold check interval in seconds.

        :param str|unicode|AlarmType alarm: Alarm to trigger when threshold is reached.

        :param str|unicode alarm_message: Message to pass to alarm. If not set metrics name is passed.

        """
        if alarm is not None and isinstance(alarm, AlarmType):
            self._section.alarms.register_alarm(alarm)
            alarm = alarm.alias

        value = make_key_val_string(
            locals(),
            aliases={
                'name': 'key',
                'reset_to': 'reset',
                'check_interval': 'rate',
                'alarm_message': 'msg',
            },
        )

        self._set('metric-threshold', value, multi=True)

        return self._section

    def set_stats_params(
            self, address=None, enable_http=None,
            minify=None, no_cores=None, no_metrics=None, push_interval=None):
        """Enables stats server on the specified address.

        * http://uwsgi.readthedocs.io/en/latest/StatsServer.html

        :param str|unicode address: Address/socket to make stats available on.

            Examples:
                * 127.0.0.1:1717
                * /tmp/statsock
                * :5050

        :param bool enable_http: Server stats over HTTP.
            Prefixes stats server json output with http headers.

        :param bool minify: Minify statistics json output.

        :param bool no_cores: Disable generation of cores-related stats.

        :param bool no_metrics: Do not include metrics in stats output.

        :param int push_interval: Set the default frequency of stats pushers in seconds/

        """
        self._set('stats-server', address)
        self._set('stats-http', enable_http, cast=bool)
        self._set('stats-minified', minify, cast=bool)
        self._set('stats-no-cores', no_cores, cast=bool)
        self._set('stats-no-metrics', no_metrics, cast=bool)
        self._set('stats-pusher-default-freq', push_interval)

        return self._section

    def register_stats_pusher(self, pusher):
        """Registers a pusher to be used for pushing statistics to various remotes/locals.

        :param Pusher|list[Pusher] pusher:

        """
        for pusher in listify(pusher):
            self._set('stats-push', pusher, multi=True)

        return self._section

    def enable_snmp(self, address, community_string):
        """Enables SNMP.

        uWSGI server embeds a tiny SNMP server that you can use to integrate
        your web apps with your monitoring infrastructure.

        * http://uwsgi.readthedocs.io/en/latest/SNMP.html

        .. note:: SNMP server is started in the master process after dropping the privileges.
            If you want it to listen on a privileged port, you can either use Capabilities on Linux,
            or use the ``as-root`` option to run the master process as root.

        :param str|unicode address: UDP address to bind to.

            Examples:

                * 192.168.1.1:2222

        :param str|unicode community_string: SNMP instance identifier to address it.

        """
        self._set('snmp', address)
        self._set('snmp-community', community_string)

        return self._section
