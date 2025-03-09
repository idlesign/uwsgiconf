from uwsgiconf.runtime.caching import *


def test_caching():

    cache = Cache('mine')

    assert cache.keys == []
    assert 'some' not in cache

    # string cast
    cache['mystr'] = 'val'
    assert cache.keys == ['mystr']
    assert cache['mystr'] == 'val'

    # deletion
    cache.delete('mystr')
    assert cache.keys == []

    # preserve bytes
    cache.set('mybytes', b'x01')
    assert cache.get('mybytes', preserve_bytes=True) == b'x01'

    # gauge
    cache.incr('myint', delta=10)
    cache.decr('myint', delta=2)
    cache.mul('myint', value=3)
    cache.div('myint', value=2)
    assert cache.get('myint', as_int=True) == 12

    # static default
    assert cache.get('some', default='other') == 'other'
    assert cache.get('int', default=10, as_int=True) == 10

    # dynamic setter
    def article_picker(key):
        if key == '1':
            return 'one'

        elif key == '2':
            return 'two'

        return None

    assert cache.get('1', setter=article_picker) == 'one'
    assert cache.get('2', setter=article_picker) == 'two'
    assert cache.get('44', default=50, setter=article_picker) == 50

    # cleaning
    cache.clear()
    assert cache.keys == []
