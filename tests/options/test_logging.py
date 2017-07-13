from uwsgiconf import Section


def test_logging_basics(assert_lines):

    logging = Section().logging

    assert_lines([
        'disable-logging = true',
        'log-format = %(method) --> %(uri)',

    ], logging.set_basic_params(
        no_requests=True,
        template='%s --> %s' % (logging.vars.REQ_METHOD, logging.vars.REQ_URL)
    ))

    assert_lines([
        'log-reopen = true',
    ], Section().logging.set_file_params(reopen_on_reload=True))

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
        'log-slow = 100',
    ], Section().logging.set_filters(slower=100))

    assert_lines([
        'log-filter = some',
    ], Section().logging.set_filters(include='some'))

    assert_lines([
        'log-drain = other',
    ], Section().logging.set_filters(exclude='other'))


def test_logging_add_logger(assert_lines):

    logging = Section().logging
    assert_lines([
        'worker-logger = my file:/home/here.log',
    ], logging.add_logger(logging.loggers.file('my', '/home/here.log'), for_single_worker=True))

    logging = Section().logging
    assert_lines([
        'logger = my socket:/home/here.sock',
    ], logging.add_logger(logging.loggers.socket('my', '/home/here.sock')))

    logging = Section().logging
    assert_lines([
        'logger = my syslog:myapp',
    ], logging.add_logger(logging.loggers.syslog('my', 'myapp')))

    logging = Section().logging
    assert_lines([
        'logger = my rsyslog:127.0.0.1:1111,myapp',
    ], logging.add_logger(logging.loggers.syslog('my', 'myapp', host='127.0.0.1:1111')))

    logging = Section().logging
    assert_lines([
        'logger = my redislog',
    ], logging.add_logger(logging.loggers.redis('my')))

    logging = Section().logging
    assert_lines([
        'logger = my mongodblog',
    ], logging.add_logger(logging.loggers.mongo('my')))

    logging = Section().logging
    assert_lines([
        'logger = my zeromq:tcp://192.168.173.18:9191',
    ], logging.add_logger(logging.loggers.zeromq('my', 'tcp://192.168.173.18:9191')))


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
    ], logger=logging.loggers.file('myfile', '/home/here.log')))
