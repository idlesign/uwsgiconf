from ..base import ParametrizedValue
from ..typehints import Strlist
from ..utils import KeyValue


class Pusher(ParametrizedValue):

    args_joiner = ','


class PusherSocket(Pusher):
    """Push metrics to a UDP server.

    Uses the following format: ``<metric> <type> <value>``
    ``<type>`` - is in the numeric form of metric type.

    """
    name = 'socket'
    plugin = 'stats_pusher_socket'

    def __init__(self, address: str, *, prefix: str | None = None):
        """
        :param address:

        :param prefix: Arbitrary prefix to differentiate sender.

        """
        super().__init__(address, prefix)


class PusherRrdtool(Pusher):
    """This will store an rrd file for each metric in the specified directory.

    Each rrd file has a single data source named "metric".

    """
    name = 'rrdtool'
    plugin = 'rrdtool'

    def __init__(self, target_dir: str, *, library: str | None = None, push_interval: int | None = None):
        """
        :param target_dir: Directory to store rrd files into.

        :param library: Set the name of rrd library. Default: librrd.so.

        :param push_interval: Set push frequency.

        """
        super().__init__(target_dir)

        self._set('rrdtool-freq', push_interval)
        self._set('rrdtool-lib', library)


class PusherStatsd(Pusher):
    """Push metrics to a statsd server."""

    name = 'statsd'
    plugin = 'stats_pusher_statsd'

    def __init__(
            self,
            address: str,
            *,
            prefix: str | None = None,
            no_workers: bool | None = None,
            all_gauges: bool | None = None
    ):
        """
        :param address:

        :param prefix: Arbitrary prefix to differentiate sender.

        :param no_workers: Disable generation of single worker metrics.

        :param all_gauges: Push all metrics to statsd as gauges.
        """
        super().__init__(address, prefix)

        self._set('statsd-no-workers', no_workers, cast=bool)
        self._set('statsd-all-gauges', all_gauges, cast=bool)


class PusherCarbon(Pusher):
    """Push metrics to a Carbon server of Graphite.

    Metric node format: ``<node_root>.hostname.<node_realm>.metrics_data``.

    * http://uwsgi.readthedocs.io/en/latest/Carbon.html
    * http://uwsgi.readthedocs.io/en/latest/tutorials/GraphiteAndMetrics.html

    """
    name = 'carbon'
    plugin = 'carbon'
    opt_key = name

    def __init__(
            self,
            address: Strlist,
            *,
            node_realm: str | None = None,
            node_root: str | None = None,
            push_interval: int | None = None,
            idle_avg_source: str | None = None,
            use_metrics: bool | None = None,
            no_workers: bool | None = None,
            timeout: int | None = None,
            retries: int | None = None,
            retries_delay: int | None = None,
            hostname_dots_replacer: str | None = None
    ):
        """
        :param address: Host and port. Example: 127.0.0.1:2004

        :param node_realm: Set carbon metrics realm node.

        :param node_root: Set carbon metrics root node. Default: uwsgi.

        :param push_interval: Set carbon push frequency in seconds. Default: 60.

        :param no_workers: Disable generation of single worker metrics.

        :param idle_avg_source: Average values source during idle period (no requests).

            Variants:
                * last (default)
                * zero
                * none

        :param use_metrics: Don't compute all statistics, use metrics subsystem data
            instead.

            .. warning:: Key names of built-in stats are different from those of metrics system.

        :param timeout: Set carbon connection timeout in seconds. Default: 3.

        :param retries: Set maximum number of retries in case of connection errors. Default: 1.

        :param retries_delay: Set connection retry delay in seconds. Default: 7.

        :param hostname_dots_replacer: Set char to use as a replacement for
            dots in hostname in `<node_root>.hostname.<node_realm>.metrics_data``

            This affects Graphite aggregation mechanics.

            .. note:: Dots are not replaced by default.

        """
        super().__init__(address)

        self._set('carbon-id', node_realm)
        self._set('carbon-root', node_root)
        self._set('carbon-freq', push_interval)
        self._set('carbon-idle-avg', idle_avg_source)
        self._set('carbon-use-metrics', use_metrics, cast=bool)
        self._set('carbon-no-workers', no_workers, cast=bool)
        self._set('carbon-timeout', timeout)
        self._set('carbon-max-retry', retries)
        self._set('carbon-retry-delay', retries_delay)
        self._set('carbon-hostname-dots', hostname_dots_replacer)

        if not address.split(':')[0].replace('.', '').isdigit():
            self._set('carbon-name-resolve', value=True, cast=bool)


class PusherZabbix(Pusher):
    """Push metrics to a zabbix server."""

    name = 'zabbix'
    plugin = 'zabbix'

    def __init__(self, address: str, *, prefix: str | None = None, template: str | None = None):
        """
        :param address:

        :param prefix: Arbitrary prefix to differentiate sender.

        :param template: Print (or store to a file) the zabbix template
            for the current metrics setup.

        """
        super().__init__(address, prefix)

        self._set('zabbix-template', template)


class PusherMongo(Pusher):
    """Push statistics (as JSON) the the specified MongoDB database."""

    name = 'mongodb'
    plugin = 'stats_pusher_mongodb'

    def __init__(self, *, address: str | None = None, collection: str | None = None, push_interval: int | None = None):
        """
        :param address: Default: 127.0.0.1:27017

        :param collection: MongoDB colection to write into. Default: uwsgi.statistics

        :param push_interval: Write interval in seconds.
        """
        value = KeyValue(locals(), aliases={'push_interval': 'freq'})

        super().__init__(value)


class PusherFile(Pusher):
    """Stores stats JSON into a file.

    .. note:: Mainly for demonstration purposes.

    """
    name = 'file'
    plugin = 'stats_pusher_file'

    def __init__(self, fpath: str | None = None, *, separator: str | None = None, push_interval: int | None = None):
        """
        :param fpath: File path. Default: uwsgi.stats

        :param separator: New entry separator. Default: \n\n

        :param push_interval: Write interval in seconds.
        """
        value = KeyValue(locals(), aliases={'fpath': 'path', 'push_interval': 'freq'})

        super().__init__(value)
