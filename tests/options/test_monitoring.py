from uwsgiconf.config import Section
from uwsgiconf.exceptions import ConfigurationError

import pytest


def test_monitoring_snmp(assert_lines):

    assert_lines([
        'snmp = 192.168.1.1:2222',
        'snmp-community = mymetr',
    ], Section().monitoring.enable_snmp('192.168.1.1:2222', 'mymetr'))


def test_monitoring_stats(assert_lines):

    assert_lines([
        'stats-server = 127.0.0.1:1717',
        'stats-http = true',
    ], Section().monitoring.set_stats_params('127.0.0.1:1717', enable_http=True))


def test_monitoring_metrics(assert_lines):

    assert_lines([
        'enable-metrics = true',
        'metrics-dir = /var/run/mine/metrics',

    ], Section(
        runtime_dir='/var/run/', project_name='mine'
    ).monitoring.set_metrics_params(enable=True, store_dir='{project_runtime_dir}/metrics'))

    assert_lines([
        'metric-threshold = alarm=some,key=mycounter,reset=0,value=1000',
    ], Section().monitoring.set_metrics_threshold('mycounter', 1000, reset_to=0, alarm='some'))

    section = Section()
    assert_lines([
        'alarm = pinger cmd:ping 127.0.0.1',
        'metric-threshold = alarm=pinger,key=mycounter,value=2000',
    ], section.monitoring.set_metrics_threshold(
        'mycounter', 2000, alarm=section.alarms.alarm_types.command('pinger', 'ping 127.0.0.1')
    ))


def test_monitoring_register_metric(assert_lines):

    monitoring = Section().monitoring

    my_abs = monitoring.metric_types.absolute('myabs', initial_value=100)
    my_abs2 = monitoring.metric_types.alias('myabs2', initial_value=200, alias_for=my_abs)

    with pytest.raises(ConfigurationError):
        # Alias without alias_for
        monitoring.metric_types.alias('myabs3', initial_value=200)

    assert_lines([
        'metric = name=myabs,initial_value=100,type=absolute',
        'metric = name=myabs2,alias=myabs,initial_value=200,type=alias',
        'metric = name=mymet,collector=sum,children=worker.1.requests;myabs,type=gauge',

    ], monitoring.register_metric([
        my_abs,
        my_abs2,
        monitoring.metric_types.gauge(
            'mymet',
            collector=monitoring.collectors.sum(['worker.1.requests', my_abs]),
        )
    ]))


def test_monitoring_collectors(assert_lines):

    collectors = Section().monitoring.collectors

    assert str(collectors.pointer()) == 'ptr'
    assert str(collectors.file('/here/a', get_slot=2)) == 'file,arg1=/here/a,arg1n=2'
    assert str(collectors.function('some')) == 'func,arg1=some'
    assert str(collectors.sum(['a', 'b'])) == 'sum,children=a;b'
    assert str(collectors.avg(['a', 'b'])) == 'avg,children=a;b'
    assert str(collectors.accumulator(['a', 'b'])) == 'accumulator,children=a;b'
    assert str(collectors.adder(['a', 'b'], 3)) == 'adder,arg1n=3,children=a;b'
    assert str(collectors.multiplier(['a', 'b'], 4)) == 'multiplier,arg1n=4,children=a;b'


def test_monitoring_pushers(assert_lines):

    monitoring = Section().monitoring
    assert_lines([
        'stats-push = socket:127.0.0.1:8125,myinstance',

    ], monitoring.register_stats_pusher(
        monitoring.pushers.socket('127.0.0.1:8125', 'myinstance')
    ))

    monitoring = Section().monitoring
    pusher = monitoring.pushers.rrdtool('/here', library='libmyrdd.so')
    assert_lines([
        'stats-push = rrdtool:/here',
        'rrdtool-lib = libmyrdd.so',

    ], monitoring.register_stats_pusher(pusher))

    monitoring = Section().monitoring
    pusher = monitoring.pushers.statsd('127.0.0.1:8125', 'myinstance', no_workers=True)
    assert_lines([
        'stats-push = statsd:127.0.0.1:8125,myinstance',
        'statsd-no-workers = true',

    ], monitoring.register_stats_pusher(
        pusher
    ))

    monitoring = Section().monitoring
    pusher = monitoring.pushers.carbon('myhost.some.net:2003')
    pusher.set_basic_params(root_node='myroot', retries=5)
    assert_lines([
        'plugin = carbon',
        'carbon-name-resolve = true',
        'carbon = myhost.some.net:2003',

    ], monitoring.register_stats_pusher(
        pusher
    ))

    monitoring = Section().monitoring
    pusher = monitoring.pushers.zabbix('127.0.0.1:10051', template='/put/here')
    assert_lines([
        'stats-push = zabbix:127.0.0.1:10051',
        'zabbix-template = /put/here',

    ], monitoring.register_stats_pusher(
        pusher
    ))

    monitoring = Section().monitoring
    assert_lines([
        'stats-push = mongodb:collection=mycol,freq=10',

    ], monitoring.register_stats_pusher(
        monitoring.pushers.mongo(collection='mycol', push_interval=10)
    ))

    monitoring = Section().monitoring
    assert_lines([
        'stats-push = file:path=/here/a.json,freq=15',

    ], monitoring.register_stats_pusher(
        monitoring.pushers.file('/here/a.json', push_interval=15)
    ))
