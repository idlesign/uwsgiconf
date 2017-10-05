from uwsgiconf.config import Section


def test_spooler_basics(assert_lines):

    assert_lines([
        'touch-spoolers-reload = /here/a',
    ], Section().spooler.set_basic_params(touch_reload='/here/a'))

    assert_lines([
        'spooler = home/one',
        'spooler = home/two',
    ], Section().spooler.add(['home/one', 'home/two']))

    assert_lines([
        'spooler-external = home/two',
    ], Section().spooler.add('home/two', external=True))
