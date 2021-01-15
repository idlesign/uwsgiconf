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


def test_get_bundled_static_path(assert_lines):

    path = Section.get_bundled_static_path('503.html')
    assert path.endswith('uwsgiconf/contrib/django/uwsgify/static/uwsgify/503.html')


def test_configure_https_redirect(assert_lines):

    section = Section()
    section.configure_https_redirect()
    assert_lines(
        'route-if-not = eq:${HTTPS};on redirect-301:https://${HTTP_HOST}${REQUEST_URI}',
        section
    )


def test_configure_maintenance_mode(assert_lines):

    section = Section()
    section.configure_maintenance_mode('/watch/that/file', '/serve/this/file')
    section.configure_maintenance_mode('/watch/that/file/also', 'http://pythonz.net')

    assert_lines([
        'route-if = exists:/watch/that/file static:/serve/this/file',
        'route-if = exists:/watch/that/file/also redirect-302:http://pythonz.net',

    ], section)


def test_configure_logging_json(assert_lines):

    section = Section()
    section.configure_logging_json()

    assert_lines([
        'logger-req = stdio:',
        'log-format = %(method) %(uri) -> %(status)',
        'log-req-encoder = json {"dt": "${strftime:%%Y-%%m-%%dT%%H:%%M:%%S%%z}", "src": "uwsgi.req"',
        'log-req-encoder = nl',
        '"src": "uwsgi.out"',

    ], section)


def test_configure_certbot_https(assert_lines, monkeypatch):

    monkeypatch.setattr('pathlib.Path.exists', lambda self: True)

    section = Section()
    section.configure_certbot_https('mydomain.org', '/var/www/', address=':4443')

    assert_lines([
        'static-map2 = /.well-known/=/var/www/',
        'https-socket = :4443,/etc/letsencrypt/live/mydomain.org/fullchain.pem,'
        '/etc/letsencrypt/live/mydomain.org/privkey.pem',
    ], section)

    section = Section.bootstrap(['http://:80'])
    section.configure_certbot_https('mydomain.org', '/var/www/', http_redirect=True)

    assert_lines([
        'shared-socket = :80',
        'shared-socket = :443',
        'http-socket = =0',
        'https-socket = =1,/etc/letsencrypt/live/mydomain.org/fullchain.pem,'
        '/etc/letsencrypt/live/mydomain.org/privkey.pem',
        'route-if-not = eq:${HTTPS};on redirect-301:https://${HTTP_HOST}${REQUEST_URI}',
    ], section)


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
