from uwsgiconf.config import Section


def test_locks_basics(assert_lines):

    assert_lines([
        'locks = 2',
    ], Section().locks.set_basic_params(count=2))

    assert_lines([
        'ftok = a',
    ], Section().locks.set_ipcsem_params(ftok='a'))

    assert_lines([
        'flock2 = /here',
    ], Section().locks.lock_file('/here', after_setup=True))

