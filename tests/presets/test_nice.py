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
        'logto',
    ], Section(), assert_in=False)

    assert_lines([
        'enable-threads = true',
        'uid = www-data',
        'gid = www-data',
        'logto = /a/b.log',

    ], Section(threads=True, log_into='/a/b.log').configure_owner())

    assert_lines([
        'workers = 13',
        'touch-reload', 'test_nice.py',

    ], Section(workers=13, touch_reload=__file__))

    assert_lines([
        'disable-write-exception = true',
        'ignore-write-errors = true',
        'ignore-sigpipe = true',
        'log-master = true',
        'threaded-logger = true',

    ], Section(log_dedicated=True, ignore_write_errors=True))

    assert '%(headers) headers in %(hsize) bytes' in Section().get_log_format_default()


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
