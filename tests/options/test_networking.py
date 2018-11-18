from uwsgiconf.config import Section


def test_networking_basics(assert_lines):

    assert_lines([
        'listen = 3',
    ], Section().networking.set_basic_params(queue_size=3))

    assert_lines([
        'so-keepalive = true',
    ], Section().networking.set_socket_params(keep_alive=True))

    assert_lines([
        'abstract-socket = true',
    ], Section().networking.set_unix_socket_params(abstract=True))

    assert_lines([
        'reuse-port = true',
    ], Section().networking.set_bsd_socket_params(port_reuse=True))

    sockets = Section.networking.sockets

    assert_lines([
        'http-socket = :8080',
        'map-socket = 0:1',
        'http-socket-modifier1 = 8',
        'http-socket-modifier2 = 1',

    ], Section().networking.register_socket(
        sockets.http(':8080', bound_workers=1, modifier=Section.routing.modifiers.jvm(submod=1))
    ))

    assert_lines([
        'socket = :8000',
        'map-socket = 0:2,3',
    ], Section().networking.register_socket(sockets.default(':8000', bound_workers=[2, 3])))

    assert_lines([
        'socket = /var/run/mine.sock',
    ], Section(
        runtime_dir='/var/run', project_name='mine'
    ).networking.register_socket(sockets.default('{project_runtime_dir}.sock')))

    assert_lines([
        'plugin = http',
        'https-export-cert = MYVAR',

    ], Section().networking.set_ssl_params(client_cert_var='MYVAR'))

    assert_lines([
        'http11-socket = :8001',
    ], Section().networking.register_socket(sockets.http(':8001', http11=True)))

    assert_lines([
        'https-socket = :8001,cert.crt,key.key,,!clientca',
    ], Section().networking.register_socket(
        sockets.https(
            ':8001', 'cert.crt', 'key.key', client_ca='!clientca')))

    assert_lines([
        'puwsgi-socket = :8001',
    ], Section().networking.register_socket(sockets.uwsgi(':8001', persistent=True)))

    assert_lines([
        'fastcgi-nph-socket = :8001',
    ], Section().networking.register_socket(sockets.fastcgi(':8001', nph=True)))

    assert_lines([
        'scgi-nph-socket = :8001',
    ], Section().networking.register_socket(sockets.scgi(':8001', nph=True)))

    shared1 = sockets.shared(':80', undeferred=True)
    shared2 = sockets.shared(':81')

    assert_lines([
            'undeferred-shared-socket = :80\nsocket = =0\nuwsgi-socket = =0',
            'shared-socket = :81\nscgi-socket = =1',
        ],
        Section().networking.register_socket([
            sockets.default(shared1),
            sockets.uwsgi(shared1),
            sockets.scgi(shared2),
        ])
    )

    assert_lines([
            'shared-socket = :80\nshared-socket = :443',
            'http = =0\nhttps2 = cert=foobar.crt,key=foobar.key,addr==1',
        ],
        Section().routing.use_router(
            Section.routing.routers.http(sockets.shared(':80'))

        ).routing.use_router(
            Section.routing.routers.https(sockets.shared(':443'), cert='foobar.crt', key='foobar.key')
        )
    )


def test_networking_sni(assert_lines):

    assert_lines([
        'sni-regexp = *.pythonz.net /here/my.crt,/here/my.key,HIGH,/there/my.ca',

    ], Section().networking.set_sni_params(
        '*.pythonz.net', cert='/here/my.crt', key='/here/my.key',
        client_ca='/there/my.ca', ciphers='HIGH',
        wildcard=True)
    )

    assert_lines([
        'sni-dir = /certs/',
        'sni-dir-ciphers = MEDIUM',

    ], Section().networking.set_sni_dir_params('/certs/', ciphers='MEDIUM'))
