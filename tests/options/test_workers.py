from uwsgiconf.config import Section


def test_workers_basics(assert_lines):

    assert_lines([
        'workers = 3',
    ], Section().workers.set_basic_params(count=3))

    assert_lines([
        'threads = 2',
    ], Section().workers.set_thread_params(count=2))

    assert_lines([
        'min-worker-lifetime = 10',
    ], Section().workers.set_reload_params(min_lifetime=10))

    assert_lines([
        'reload-on-exception = true',
    ], Section().workers.set_reload_on_exception_params(do_reload=True))

    assert_lines([
        'harakiri = 20',
    ], Section().workers.set_harakiri_params(timeout=20))

    assert_lines([
        'worker-exec = date',
    ], Section().workers.run_command_as_worker('date'))


def test_mules(assert_lines):

    assert_lines([
        'mule-harakiri = 3',
    ], Section().workers.set_mules_params(harakiri_timeout=3))

    section = Section()
    assert_lines([
        'farm = first:1,2',
        'farm = second:3,4,5',
        'mules = 5',

    ], section.workers.set_mules_params(farms=[
        section.workers.mule_farm('first', 2),
        section.workers.mule_farm('second', 3),
    ]))

    section = Section()
    assert_lines([
        'farm = first:1',
        'farm = second:2,3,4',
        'mules = 4',

    ], section.workers.set_mules_params(farms=[
        section.workers.mule_farm('first', [1]),
        section.workers.mule_farm('second', [2, 3, 4]),
    ]))

    assert_lines([
        'mule = mule1.py',
        'mule = mule2.py',

    ], Section().workers.set_mules_params(mules=[
        'mule1.py',
        'mule2.py',
    ]))


def test_zergs(assert_lines):

    assert_lines([
        'zerg-server = /here',
    ], Section().workers.set_zerg_server_params('/here'))

    assert_lines([
        'zergpool = /here:127.0.0.1:3031,127.0.0.1:3032',
    ], Section().workers.set_zerg_server_params(
        '/here', clients_socket_pool=['127.0.0.1:3031', '127.0.0.1:3032']))

    assert_lines([
        'zerg = /here',
        'zerg = /there',
        'zerg-fallback = true',
        'socket = /here',
        'socket = /there',

    ], Section().workers.set_zerg_client_params(
        ['/here', '/there'], use_fallback_socket=True
    ))


def test_cheapening(assert_lines):

    assert_lines([
        'cheaper-algo = manual',
    ], Section().cheapening.set_basic_params(cheaper_algo=Section.cheapening.algorithms.manual()))

    assert_lines([
        'cheaper-algo = spare',
        'cheaper-overload = 20',
    ], Section().cheapening(cheaper_algo=Section.cheapening.algorithms.spare(check_interval_overload=20)))

    assert_lines([
        'cheaper-algo = spare2',
        'cheaper-idle = 10',
    ], Section().cheapening(cheaper_algo=Section.cheapening.algorithms.spare2(check_interval_idle=10)))

    assert_lines([
        'cheaper-algo = backlog',
        'cheaper-overload = 30',
    ], Section().cheapening(cheaper_algo=Section.cheapening.algorithms.queue(check_num_overload=30)))

    assert_lines([
        'plugin = cheaper_busyness',
        'cheaper-busyness-max = 25',
        'cheaper-busyness-backlog-step = 3',
    ], Section().cheapening(
        cheaper_algo=Section.cheapening.algorithms.busyness(busy_max=25).set_emergency_params(workers_step=3)
    ))

    assert_lines([
        'cheaper-rss-limit-soft = 1024',
    ], Section().cheapening.set_memory_limits(rss_soft=1024))

    assert_lines([
        'cheaper-algo-list = true',
    ], Section().cheapening.print_alorithms())
