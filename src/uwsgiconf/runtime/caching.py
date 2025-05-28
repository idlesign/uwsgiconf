from collections.abc import Callable
from typing import Any

from .. import uwsgi
from ..typehints import Strint
from ..utils import decode, decode_deep


class Cache:
    """Interface for uWSGI Caching subsystem.

    .. warning:: To use this helper one needs
        to configure cache(s) in uWSGI config beforehand.

        E.g.: ``section.caching.add_cache('mycache', 100)``

    """
    __slots__ = ['name', 'timeout']

    def __init__(self, name: str, *, timeout: int | None = None):
        """
        :param name: Cache name with optional address (if @-syntax is used).

        :param timeout: Expire timeout (seconds).
            Default: 300 (5 minutes). Use 0 for no expire.

            .. note:: This value is ignored if cache is configured not to expire.

        """
        self.timeout = timeout or 300
        self.name = name

    def __contains__(self, key: str) -> bool:
        """Checks whether there is a value in the cache associated with the given key.

        :param key: The cache key to check.

        """
        return uwsgi.cache_exists(key, self.name)

    @property
    def keys(self) -> list[str]:
        """Returns a list of keys available in cache.

        :raises ValueError: If cache is unavailable.

        """
        return decode_deep(uwsgi.cache_keys(self.name))

    def clear(self):
        """Clears cache the cache."""
        uwsgi.cache_clear(self.name)

    def get(
            self,
            key: str,
            *,
            default: Any = None,
            as_int: bool = False,
            setter: Callable[[str], Any] | None = None,
            preserve_bytes: bool = False,

    ) -> Strint | bytes:
        """Gets a value from the cache.

        :param key: The cache key to get value for.

        :param default: Value to return if none found in cache.

        :param as_int: Return 64bit number instead of a str.
            To be used with `incr`, `decr`, `mul`, `div`.

        :param setter: Setter callable to automatically set cache
            value if not already cached. Required to accept a key and return
            a value that will be cached.

        :param preserve_bytes: If True, bytes representation is returned.

        """
        if as_int:
            val = uwsgi.cache_num(key, self.name)

        else:
            val = uwsgi.cache_get(key, self.name)
            if not preserve_bytes:
                val = decode(val)

        if val is None:  # no cache entry

            if setter is None:
                return default

            val = setter(key)

            if val is None:
                return default

            self.set(key, val)

        return val

    __getitem__ = get

    def set(self, key: str, value: Any, *, timeout: int | None = None) -> bool:
        """Sets the specified key value.

        :param key: Cache key to set.

        :param value: Value to store in cache.
            .. note:: This value will be casted to str->bytes (as uWSGI cache works with bytes-like objects).

        :param timeout: 0 not to expire. Object default is used if not set.

        """
        if timeout is None:
            timeout = self.timeout

        if not isinstance(value, bytes):
            value = f'{value}'.encode()

        return uwsgi.cache_set(key, value, timeout, self.name)

    __setitem__ = set

    def delete(self, key: str):
        """Deletes the given cached key from the cache.

        :param key: The cache key to delete.

        """
        uwsgi.cache_del(key, self.name)

    __delitem__ = delete

    def incr(self, key: str, *, delta: int = 1) -> bool:
        """Increments the specified key value by the specified value.
       
        :param key:
    
        :param delta:

        """
        return uwsgi.cache_inc(key, delta, self.timeout, self.name)

    def decr(self, key: str, *, delta: int = 1) -> bool:
        """Decrements the specified key value by the specified value.

        :param key:

        :param delta:

        """
        return uwsgi.cache_dec(key, delta, self.timeout, self.name)

    def mul(self, key: str, *, value: int = 2) -> bool:
        """Multiplies the specified key value by the specified value.

        :param key:

        :param value:

        """
        return uwsgi.cache_mul(key, value, self.timeout, self.name)

    def div(self, key: str, *, value: int = 2) -> bool:
        """Divides the specified key value by the specified value.

        :param key:

        :param value:

        """
        return uwsgi.cache_div(key, value, self.timeout, self.name)
