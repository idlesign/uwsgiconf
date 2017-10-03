from uwsgiconf.presets.nice import Section, PythonSection


def test_nice_section(assert_lines):

    assert_lines([
        'env = LANG=en_US.UTF-8',
        'workers = %k',
        'die-on-term = true',
        'vacuum = true',
        'threads = 4',

    ], Section(threads=4))

    assert_lines([
        'enable-threads = true',
        'uid = www-data',
        'gid = www-data',

    ], Section(threads=True).configure_owner())

    assert_lines([
        'workers = 13',
        'touch-reload', 'test_nice.py',

    ], Section(workers=13, touch_reload=__file__))


def test_nice_python(assert_lines):

    assert_lines([
        'plugin = python',
        'pyhome = /home/idle/venv/\npythonpath = /home/idle/apps/',
        'wsgi = somepackage.module',
        'need-app = true',

    ], PythonSection(
        params_python=dict(
            # We'll run our app using virtualenv.
            python_home='/home/idle/venv/',
            search_path='/home/idle/apps/',
        ),
        wsgi_module='somepackage.module',
        embedded_plugins=None
    ))

    # Embedded plugins = True
    assert_lines('plugin = python', PythonSection(wsgi_module='somepackage.module'), assert_in=False)
