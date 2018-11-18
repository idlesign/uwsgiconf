from uwsgiconf.config import Section


def test_spooler_basics(assert_lines):

    assert_lines([
        'touch-spoolers-reload = /here/a',
    ], Section().spooler.set_basic_params(touch_reload='/here/a'))

    assert_lines([
        'spooler = /var/run/mine/one',
        'spooler = /var/run/mine/two',

    ], Section(
        runtime_dir='/var/run/', project_name='mine'
    ).spooler.add(work_dir=['{project_runtime_dir}/one', '{project_runtime_dir}/two']))

    assert_lines([
        'spooler-external = home/two',
    ], Section().spooler.add('home/two', external=True))
