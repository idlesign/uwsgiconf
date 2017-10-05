import pytest

from uwsgiconf.config import Section
from uwsgiconf.exceptions import ConfigurationError


def test_subscriptions_basics(assert_lines):

    assert_lines([
        'subscription-mountpoint = 2',
    ], Section().subscriptions.set_server_params(mountpoints_depth=2))

    assert_lines([
        'subscriptions-sign-check',
    ], Section().subscriptions.set_server_verification_params(digest_algo='SHA1'), assert_in=False)

    assert_lines([
        'subscriptions-sign-check = SHA1:/here',
        'subscriptions-sign-skip-uid = 1001',
        'subscriptions-sign-skip-uid = 1002',
    ], Section().subscriptions.set_server_verification_params(
        digest_algo='SHA1', dir_cert='/here', no_check_uid=[1001, 1002]))

    assert_lines([
        'start-unsubscribed = true',
    ], Section().subscriptions.set_client_params(start_unsubscribed=True))

    # Subscribing:

    with pytest.raises(ConfigurationError):  # both key and server omitted
        Section().subscriptions.subscribe(balancing_weight=2)

    assert_lines([
        'key=pythonz.net',
        'server=127.0.0.1:4040',
    ], Section().subscriptions.subscribe('127.0.0.1:4040', 'pythonz.net'))

    # SNI
    assert_lines([
        'socket=0',
        'key=mydomain.it',
        'sni_crt=/foo/bar.crt,sni_key=/foo/bar.key',
    ], Section().subscriptions.subscribe(key='mydomain.it', address=0, sni_cert='/foo/bar.crt', sni_key='/foo/bar.key'))

    # algos
    algo = Section.subscriptions.algorithms.weighted_least_reference_count(2)
    assert_lines([
        'backup=2',
        'algo=wlrc',
    ], Section().subscriptions.subscribe('127.0.0.1:4040', balancing_algo=algo))

    # modifiers
    assert_lines([
        'modifier1=31',
        'modifier2=42',
    ], Section().subscriptions.subscribe('127.0.0.1:4040', modifier=Section.routing.modifiers.message(42)))

    # signing
    assert_lines([
        'sign=SHA1:myssh001',
    ], Section().subscriptions.subscribe('127.0.0.1:4040', signing=('SHA1', 'myssh001')))
