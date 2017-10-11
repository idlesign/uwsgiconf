from uwsgiconf.config import Section


def test_http(assert_lines):

    routers = Section.routing.routers

    router = routers.http(
        on='127.0.0.1:3111'
    ).set_basic_params(
        keepalive=20
    ).set_connections_params(
        harakiri=20
    ).set_manage_params(
        websockets=True
    ).set_owner_params('idle')

    assert_lines([
        'http = 127.0.0.1:3111',
        'http-keepalive = 20',
        'http-harakiri = 20',
        'http-websockets = true',
        'http-uid = idle',
        ],
        Section().routing.use_router(router)
    )

    router = routers.https(
        on='127.0.0.1:3112',
        cert='/here/mysert.cer',
        key='mykey',
        session_context='somectx')

    assert_lines([
        'https2 = cert=/here/mysert.cer,key=mykey,addr=127.0.0.1:3112',
        'http-session-context = somectx',
        ],
        Section().routing.use_router(router)
    )


def test_ssl(assert_lines):

    routers = Section.routing.routers

    router = routers.ssl(
        on='127.0.0.1:3112',
        cert='/here/mysert.cer',
        key='mykey',
    ).set_connections_params(
        retry_max=5
    )

    assert_lines([
        'sslrouter2 = cert=/here/mysert.cer,key=mykey,addr=127.0.0.1:3112',
        'sslrouter-max-retries = 5',
        ],
        Section().routing.use_router(router)
    )


def test_raw(assert_lines):

    routers = Section.routing.routers

    router = routers.raw(
        on='127.0.0.1:3115'
    ).set_connections_params(
        retry_max=5
    )

    assert_lines([
        'rawrouter = 127.0.0.1:3115',
        'rawrouter-max-retries = 5',
        ],
        Section().routing.use_router(router)
    )


def test_fast(assert_lines):

    routers = Section.routing.routers

    router = routers.fast(
        on='127.0.0.1:3113',
        forward_to=['127.0.0.1:3123', '127.0.0.1:3124'],
    ).set_connections_params(
        defer=5
    ).set_resubscription_params(
        addresses='127.0.0.1:3114'
    ).set_postbuffering_params(
        size=100
    ).set_owner_params('idle')

    assert_lines([
        'fastrouter = 127.0.0.1:3113',
        'fastrouter-to = 127.0.0.1:3123',
        'fastrouter-to = 127.0.0.1:3124',
        'fastrouter-defer-connect-timeout = 5',
        'fastrouter-resubscribe = 127.0.0.1:3114',
        'fastrouter-post-buffering = 100',
        'fastrouter-uid = idle',
        ],
        Section().routing.use_router(router)
    )


def test_forkpty(assert_lines):

    routers = Section.routing.routers

    router = routers.forkpty(
        on='127.0.0.1:3118',
        undeferred=True
    ).set_basic_params(
        run_command='/bin/zsh'
    ).set_connections_params(
        timeout_socket=13
    ).set_window_params(cols=10, rows=15)

    assert_lines([
        'forkptyurouter = 127.0.0.1:3118',
        'forkptyrouter-timeout = 13',
        'forkptyrouter-cols = 10',
        'forkptyrouter-rows = 15',
        ],
        Section().routing.use_router(router)
    )


def test_tuntap(assert_lines):

    routers = Section.routing.routers

    router = routers.tuntap(
        on='/tmp/tuntap.socket',
        device='emperor0',
        stats_server='127.0.0.1:3030',
        gateway='127.0.0.1:3032',
    ).set_basic_params(
        use_credentials='some'
    ).add_firewall_rule(
        direction='out',
        action='allow',
        src='192.168.0.0/24',
        dst='192.168.0.1',
    ).register_route(
        src='192.168.0.1/24',
        dst='192.168.0.2',
        gateway='192.168.0.4',
    )

    assert_lines([
        'tuntap-use-credentials = some',
        'tuntap-router = emperor0 /tmp/tuntap.socket 127.0.0.1:3030 127.0.0.1:3032',
        'tuntap-router-firewall-out = allow 192.168.0.0/24 192.168.0.1',
        'tuntap-router-route = 192.168.0.1/24 192.168.0.2 192.168.0.4',
        ],
        Section().routing.use_router(router)
    )

    router = routers.tuntap().device_connect(
        device_name='uwsgi0',
        socket='/tmp/tuntap.socket',
    ). device_add_rule(
        direction='in',
        action='route',
        src='192.168.0.1',
        dst='192.168.0.2',
        target='10.20.30.40:5060',
    )

    assert_lines([
        'tuntap-device = uwsgi0 /tmp/tuntap.socket',
        'tuntap-device-rule = in 192.168.0.1 192.168.0.2 route 10.20.30.40:5060',
        ],
        Section().routing.use_router(router)
    )


def test_forwarders(assert_lines):

    routers = Section.routing.routers

    router = routers.fast
    assert_lines(
        'fastrouter-use-base = /tmp/sockets/',

        Section().routing.use_router(router(on='127.0.0.1:3110',
            forward_to=router.forwarders.path('/tmp/sockets/'))))

    assert_lines(
        'fastrouter-use-pattern = /tmp/sockets/%s/uwsgi.sock',

        Section().routing.use_router(router(on='127.0.0.1:3110',
            forward_to=router.forwarders.path('/tmp/sockets/%s/uwsgi.sock'))))

    assert_lines(
        'fastrouter-use-code-string = 0:some.py:funcname',

        Section().routing.use_router(router(on='127.0.0.1:3110',
            forward_to=router.forwarders.code('some.py', 'funcname'))))

    assert_lines(
        'fastrouter-use-cache = mine',

        Section().routing.use_router(router(on='127.0.0.1:3110',
            forward_to=router.forwarders.cache('mine'))))

    assert_lines(
        'fastrouter-use-socket = /there/here.sock',

        Section().routing.use_router(router(on='127.0.0.1:3110',
            forward_to=router.forwarders.socket('/there/here.sock'))))

    assert_lines(
        'fastrouter-subscription-server = 192.168.0.100:7000',

        Section().routing.use_router(router(on='127.0.0.1:3110',
            forward_to=router.forwarders.subscription_server('192.168.0.100:7000'))))
