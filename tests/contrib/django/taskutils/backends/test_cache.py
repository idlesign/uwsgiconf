import pytest
from django.core.cache.backends.base import InvalidCacheBackendError

from uwsgiconf.contrib.django.uwsgify.taskutils.backends import CacheBackend
from uwsgiconf.contrib.django.uwsgify.taskutils.decorators import task


def mytask():
    return 'some'


def test_cache():

    # fine
    task_1 = task(backend=CacheBackend(cache_name='default'))(mytask)
    assert task_1() == 'some'

    # unknown backend
    task_2 = task(backend=CacheBackend(cache_name='unknown'))(mytask)

    with pytest.raises(InvalidCacheBackendError):
        task_2()

    # unknown backend silenced
    task_3 = task(backend=CacheBackend(cache_name='unknown', strict=False))(mytask)
    assert task_3() is None
