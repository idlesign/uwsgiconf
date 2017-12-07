from uwsgiconf.config import Section


def test_logging_basics(assert_lines):

    logging = Section().logging

    assert_lines([
        'disable-logging = true',
        'log-format = %(method) --> %(uri) %(metric.my) %(var.X_REQUEST_ID)',
        'log-date = true',

    ], logging.set_basic_params(
        no_requests=True,
        template='%s --> %s %s %s' % (
            logging.vars.REQ_METHOD,
            logging.vars.REQ_URI,
            logging.vars.metric('my'),
            logging.vars.request_var('X-Request-Id'),
        ),
        prefix_date=True
    ))

    assert_lines([
        'logformat-strftime = true',
        'log-date = %%Y-%%M-%%D',

    ], Section().logging.set_basic_params(
        prefix_date='%Y-%M-%D',
        apply_strftime=True,
    ))

    assert_lines([
        'log-reopen = true',
    ], Section().logging.set_file_params(reopen_on_reload=True))

    assert_lines([
        'logto2 = /a/b.log',
    ], Section().logging.log_into('/a/b.log', before_priv_drop=False))

    assert_lines([
        'log-master = true',
        'log-master-req-stream = true',
    ], Section().logging.set_master_logging_params(
        enable=True, sock_stream_requests_only=True))

    assert_lines([
        'loggers-list = true',
    ], Section().logging.print_loggers())

    assert_lines([
        'log-route = socket aline',
    ], Section().logging.add_logger_route('socket', 'aline'))


def test_logging_set_filters(assert_lines):
    assert_lines([
        'log-filter = some',
    ], Section().logging.set_filters(include='some'))

    assert_lines([
        'log-drain = other',
    ], Section().logging.set_filters(exclude='other'))

    assert_lines([
        'ignore-write-errors = true',
        'ignore-sigpipe = true',
    ], Section().logging.set_filters(write_errors=False, sigpipe=False))

    assert_lines('ignore-write-errors = true', Section().logging.set_filters(write_errors=True), assert_in=False)


def test_logging_set_requests_filters(assert_lines):

    assert_lines([
        'log-slow = 100',
    ], Section().logging.set_requests_filters(slower=100))

    assert_lines([
        'log-ioerror = true',
    ], Section().logging.set_requests_filters(io_errors=True))

    assert_lines('ignore-write-errors = true', Section().logging.set_filters(write_errors=True), assert_in=False)


def test_logging_add_logger(assert_lines):

    logging = Section().logging
    assert_lines([
        'worker-logger = my file:/home/here.log',
    ], logging.add_logger(logging.loggers.file('/home/here.log', alias='my'), for_single_worker=True))

    logging = Section().logging
    assert_lines([
        'logger = file:/home/there.log',
    ], logging.add_logger(logging.loggers.file('/home/there.log')))

    logging = Section().logging
    assert_lines([
        'logger = my socket:/home/here.sock',
    ], logging.add_logger(logging.loggers.socket('/home/here.sock', alias='my')))

    logging = Section().logging
    assert_lines([
        'logger = my syslog:myapp',
    ], logging.add_logger(logging.loggers.syslog('myapp', alias='my')))

    logging = Section().logging
    assert_lines([
        'plugin = syslog',
        'logger = my syslog:myapp,local6',
    ], logging.add_logger(logging.loggers.syslog('myapp', facility='local6', alias='my')))

    logging = Section().logging
    assert_lines([
        'plugin = rsyslog',
        'rsyslog-packet-size = 1024',
        'logger = my rsyslog:127.0.0.1:1111,myapp',
    ], logging.add_logger(logging.loggers.rsyslog('myapp', '127.0.0.1:1111', packet_size=1024, alias='my')))

    logging = Section().logging
    assert_lines([
        'logger = my redislog',
    ], logging.add_logger(logging.loggers.redis(alias='my')))

    logging = Section().logging
    assert_lines([
        'logger = my mongodblog',
    ], logging.add_logger(logging.loggers.mongo(alias='my')))

    logging = Section().logging
    assert_lines([
        'logger = my zeromq:tcp://192.168.173.18:9191',
    ], logging.add_logger(logging.loggers.zeromq('tcp://192.168.173.18:9191', alias='my')))


def test_logging_add_logger_encoder(assert_lines):

    logging = Section().logging

    assert_lines([
        'worker-log-encoder = prefix -->',
        'worker-log-encoder = suffix <--',

    ], logging.add_logger_encoder([
        logging.encoders.prefix('-->'),
        logging.encoders.suffix('<--'),
    ], for_single_worker=True))

    logging = Section().logging
    enc_format = logging.encoders.format

    assert_lines([
        'log-encoder = format > ${msg} <:myfile',

    ], logging.add_logger_encoder([
        enc_format('> %s <' % enc_format.vars.MESSAGE),
    ], logger=logging.loggers.file('/home/here.log', alias='myfile')))
