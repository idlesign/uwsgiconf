from uwsgiconf import Section


def test_applications_basics(assert_lines):

    assert_lines([
        'need-app = true',
    ], Section().applications.set_basic_params(exit_if_none=True))

    assert_lines([
        'chdir = /here',
    ], Section().applications.change_dir('/here'))

    assert_lines([
        'mount = /articles=app.py',
    ], Section().applications.mount('/articles', 'app.py'))

    assert_lines([
        'idle = 10',
    ], Section().applications.set_idle_params(timeout=10))

    assert_lines([
        'lazy-apps = true',
    ], Section().applications.switch_into_lazy_mode())
