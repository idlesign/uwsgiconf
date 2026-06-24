from django.core.cache.backends.base import DEFAULT_TIMEOUT

from uwsgiconf.contrib.django.uwsgify.cache import UwsgiCache


def test_cache():
    from django.core.cache import cache

    assert cache.get("some") is None
    assert not cache.touch("some")
    cache.set("some", 1)
    assert cache.touch("some")

    assert cache.get("some") == 1
    cache.incr("some", delta=2)
    assert cache.get("some") == 3

    cache.add("other", [1, 2, 3])
    assert cache.get("other") == [1, 2, 3]

    assert cache.has_key("other")
    cache.delete("other")
    assert not cache.has_key("other")

    cache.clear()
    assert not cache.has_key("some")


def test_cache_default_timeout_is_resolved():
    cache = UwsgiCache("some", {})

    assert cache._resolve_uwsgi_timeout(DEFAULT_TIMEOUT) == 300


def test_cache_none_timeout_never_expires():
    cache = UwsgiCache("some", {"TIMEOUT": None})

    assert cache._resolve_uwsgi_timeout(DEFAULT_TIMEOUT) == 0
    assert cache._resolve_uwsgi_timeout(None) == 0
