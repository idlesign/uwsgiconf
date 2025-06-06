
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
