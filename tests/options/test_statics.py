from uwsgiconf.config import Section


def test_statics_basics(assert_lines):

    assert_lines([
        'static-index = index.html',
    ], Section().statics.set_basic_params(index_file='index.html'))

    assert_lines([
        'check-static-docroot = true',
    ], Section().statics.set_basic_params(static_dir=Section.statics.DIR_DOCUMENT_ROOT))

    assert_lines([
        'static-map2 = /static=/var/www/static',
        'static-safe = /var/www/static',

    ], Section().statics.register_static_map(
        '/static', '/var/www/static', retain_resource_path=True, safe_target=True
    ))

    assert_lines([
        'static-cache-paths = 200',
    ], Section().statics.set_paths_caching_params(timeout=200))


def test_statics_expiration(assert_lines):

    statics = Section().statics

    assert_lines([
        'static-expires-mtime = .*png 50',
        'static-expires-mtime = .*pdf 50',
        'static-expires-type = text/html=100',

    ],
    statics.add_expiration_rule(
        statics.expiration_criteria.FILENAME, ['.*png', '.*pdf'], 50, use_mod_time=True

    ).statics.add_expiration_rule(
        statics.expiration_criteria.MIME_TYPE, 'text/html', 100

    ))

