from ..base import OptionsGroup
from ..utils import KeyValue, listify
from .alarms import AlarmType
from .monitoring_collectors import *
from .monitoring_metric_types import *
from .monitoring_pushers import *


class Monitoring(OptionsGroup):
    """Monitoring facilities.

    * SNMP - http://uwsgi.readthedocs.io/en/latest/SNMP.html

    * Stats - http://uwsgi.readthedocs.io/en/latest/StatsServer.html
        Set of metrics gathered from uWSGI internals.

    * Metrics - http://uwsgi.readthedocs.io/en/latest/Metrics.html
        Basic set of metrics gathered from uWSGI internals + user defined metrics.

    """
    class metric_types:
        """Various metric types to represent data of various nature.

        User metrics must inherit from one of those.

        """
        absolute = MetricTypeAbsolute
        alias = MetricTypeAlias
        counter = MetricTypeCounter
        gauge = MetricTypeGauge

    class collectors:
        """Metric collection and accumulation means."""

        accumulator = CollectorAccumulator
        adder = CollectorAdder
        avg = CollectorAvg
        file = CollectorFile
        function = CollectorFunction
        multiplier = CollectorMultiplier
        pointer = CollectorPointer
        sum = CollectorSum

    class pushers:
        """Means to deliver metrics to various remotes or locals.

        These are available for ``.register_stats_pusher()``.

        """
        carbon = PusherCarbon
        file = PusherFile
        mongo = PusherMongo
        rrdtool = PusherRrdtool
        socket = PusherSocket
        statsd = PusherStatsd
        zabbix = PusherZabbix

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
        for metric_ in listify(metric):
            self._set('metric', metric_, multi=True)

        return self._section

    def set_metrics_params(
            self,
            *,
            enable: bool | None = None,
            store_dir: str | None = None,
            restore: bool | None = None,
            no_cores: bool | None = None
    ):
        """Sets basic Metrics subsystem params.

        uWSGI metrics subsystem allows you to manage "numbers" from your apps.

        When enabled, the subsystem configures a vast amount of metrics
        (like requests per-core, memory usage, etc.) but, in addition to this,
        you can configure your own metrics, such as the number of active users or, say,
        hits of a particular URL, as well as the memory consumption of your app or the whole server.

        * http://uwsgi.readthedocs.io/en/latest/Metrics.html
        * SNMP Integration - http://uwsgi.readthedocs.io/en/latest/Metrics.html#snmp-integration

        :param enable: Enables the subsystem.

        :param store_dir: Directory to store metrics.
            The metrics subsystem can expose all of its metrics in the form
            of text files in a directory. The content of each file is the value
            of the metric (updated in real time).

            .. note:: Placeholders can be used to build paths, e.g.: {project_runtime_dir}/metrics/
              See ``Section.project_name`` and ``Section.runtime_dir``.

        :param restore: Restore previous metrics from ``store_dir``.
            When you restart a uWSGI instance, all of its metrics are reset.
            Use the option to force the metric subsystem to read-back the values
            from the metric directory before starting to collect values.

        :param no_cores: Disable generation of cores-related metrics.

        """
        self._set('enable-metrics', enable, cast=bool)
        self._set('metrics-dir', self._section.replace_placeholders(store_dir))
        self._set('metrics-dir-restore', restore, cast=bool)
        self._set('metrics-no-cores', no_cores, cast=bool)

        return self._section

    def set_metrics_threshold(
            self,
            name: str,
            value: str,
            *,
            check_interval: int | None = None,
            reset_to: int | None = None,
            alarm=None,
            alarm_message: str | None = None
    ):
        """Sets metric threshold parameters.

        :param name: Metric name.

        :param value: Threshold value.

        :param reset_to: Reset value to when threshold is reached.

        :param check_interval: Threshold check interval in seconds.

        :param str|AlarmType alarm: Alarm to trigger when threshold is reached.

        :param alarm_message: Message to pass to alarm. If not set metrics name is passed.

        """
        if alarm is not None and isinstance(alarm, AlarmType):
            self._section.alarms.register_alarm(alarm)
            alarm = alarm.alias

        value = KeyValue(
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
            self,
            address: str | None = None,
            *,
            enable_http: bool | None = None,
            minify: bool | None = None,
            no_cores: bool | None = None,
            no_metrics: bool | None = None,
            push_interval: int | None = None
    ):
        """Enables stats server on the specified address.

        * http://uwsgi.readthedocs.io/en/latest/StatsServer.html

        :param address: Address/socket to make stats available on.

            Examples:
                * 127.0.0.1:1717
                * /tmp/statsock
                * :5050

        :param enable_http: Server stats over HTTP.
            Prefixes stats server json output with http headers.

        :param minify: Minify statistics json output.

        :param no_cores: Disable generation of cores-related stats.

        :param no_metrics: Do not include metrics in stats output.

        :param push_interval: Set the default frequency of stats pushers in seconds/

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
        for pusher_ in listify(pusher):
            self._set('stats-push', pusher_, multi=True)

        return self._section

    def enable_snmp(self, address: str, community_string: str):
        """Enables SNMP.

        uWSGI server embeds a tiny SNMP server that you can use to integrate
        your web apps with your monitoring infrastructure.

        * http://uwsgi.readthedocs.io/en/latest/SNMP.html

        .. note:: SNMP server is started in the master process after dropping the privileges.
            If you want it to listen on a privileged port, you can either use Capabilities on Linux,
            or use the ``as-root`` option to run the master process as root.

        :param str address: UDP address to bind to.

            Examples:

                * 192.168.1.1:2222

        :param str community_string: SNMP instance identifier to address it.

        """
        self._set('snmp', address)
        self._set('snmp-community', community_string)

        return self._section
