import pytest

from uwsgiconf import Section
from uwsgiconf.exceptions import ConfigurationError


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

    assert_lines([
        'http-socket = :8080',
        'map-socket = 0:1',
    ], Section().networking.register_socket(
        address=':8080', type=Section.networking.socket_types.HTTP,
        bound_workers=1))

    assert_lines([
        'socket = :8000',
        'map-socket = 0:2,3',
    ], Section().networking.register_socket(address=':8000', bound_workers=[2, 3]))

    with pytest.raises(ConfigurationError) as einfo:
        assert_lines([
            '',
        ], Section().networking.register_socket(address='127.0.0.1', type='dummy'))
    assert 'Unknown' in str(einfo.value)  # unknown socket type

    # batch socket registration
    assert_lines([
        'socket = :8001',
        'socket = :8002',
        'socket = :8003',

    ], Section().networking.register_sockets(
        dict(address=':8001'),
        dict(address=':8002'),
        dict(address=':8003'),
    ))

    assert_lines([
        'plugin = http',
        'https-export-cert = MYVAR',

    ], Section().networking.set_ssl_params(client_cert_var='MYVAR'))


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
