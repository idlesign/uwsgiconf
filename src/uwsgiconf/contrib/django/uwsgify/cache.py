import pickle
from typing import Any

from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache
from uwsgiconf.runtime.caching import Cache as _Cache


class UwsgiCache(BaseCache):
    """
    Configuration example:
        CACHES = {
            "default": {
                "BACKEND": "uwsgiconf.contrib.django.uwsgify.cache.UwsgiCache",
                "LOCATION": "mycache",
            }
        }
    """

    def __init__(self, name: str, params: dict):
        super().__init__(params)
        self._cache = _Cache(name)

    def _set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        self._cache.set(
            self.make_and_validate_key(key, version=version),
            pickle.dumps(value),
            timeout=timeout
        )

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None) -> bool:
        self._set(key, value, timeout=timeout, version=version)
        return True

    def get(self, key, default=None, version=None) -> Any:
        value = self._cache.get(
            self.make_and_validate_key(key, version=version),
            default=default,
            preserve_bytes=True
        )
        return pickle.loads(value) if (value is not None and value is not default) else default

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        self._set(key, value, timeout=timeout, version=version)

    def touch(self, key, timeout=DEFAULT_TIMEOUT, version=None) -> bool:
        obj = object()

        value = self.get(key, default=obj, version=version)
        if value is obj:
            return False

        self._set(key, value, timeout=timeout, version=version)
        return True

    def delete(self, key, version=None) -> bool:
        self._cache.delete(self.make_and_validate_key(key, version=version))
        return True

    def has_key(self, key, version=None) -> bool:
        return self.make_and_validate_key(key, version=version) in self._cache

    def clear(self):
        self._cache.clear()
