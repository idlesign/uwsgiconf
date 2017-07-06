from uwsgiconf import Section


def test_applications_basics(assert_lines):

    assert_lines([
        'need-app = true',
    ], Section().grp_applications.set_basic_params(exit_if_none=True))

    assert_lines([
        'chdir = /here',
    ], Section().grp_applications.change_dir('/here'))

    assert_lines([
        'mount = /articles=app.py',
    ], Section().grp_applications.mount('/articles', 'app.py'))

    assert_lines([
        'idle = 10',
    ], Section().grp_applications.set_idle_params(timeout=10))

    assert_lines([
        'lazy-apps = true',
    ], Section().grp_applications.switch_into_lazy_mode())
