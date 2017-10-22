from uwsgiconf.runtime.caching import *


def test_caching():

    cache = Cache('mine')

    keys = cache.keys

    cache.clear()

    cache.set('my', 10)
    cache.incr('my')
    cache.decr('my')
    cache.mul('my')
    cache.div('my')
    cache.delete('my')

    assert cache.get('some', 'other') == 'other'
    assert cache.get('int', 10, as_int=True) == 10

    assert 'some' not in cache

    def article_picker(key):
        if key == '1':
            return 'one'

        elif key == '2':
            return 'two'

        return None

    assert cache.get('1', setter=article_picker) == 'one'
    assert cache.get('2', setter=article_picker) == 'two'
    assert cache.get('44', default=50, setter=article_picker) == 50
