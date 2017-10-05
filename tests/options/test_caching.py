from uwsgiconf.config import Section


def test_caching_basics(assert_lines):

    assert_lines([
        'cache-no-expire = true',
    ], Section().caching.set_basic_params(no_expire=True))

    assert_lines([
        'add-cache-item = a=b',
    ], Section().caching.add_item('a', 'b'))

    assert_lines([
        'add-cache-item = some a=b',
    ], Section().caching.add_item('a', 'b', cache_name='some'))

    assert_lines([
        'load-file-in-cache = /home/some.a',
    ], Section().caching.add_file('/home/some.a'))

    assert_lines([
        'load-file-in-cache-gzip = /home/some.a',
    ], Section().caching.add_file('/home/some.a', gzip=True))

    assert_lines([
        'load-file-in-cache = some /home/some.a',
    ], Section().caching.add_file('/home/some.a', cache_name='some'))

    assert_lines([
        'cache2 = name=mine,maxitems=333',
    ], Section().caching.add_cache('mine', 333))

