from .. import uwsgi
from ..utils import decode

# todo: may be cache_update


class Cache(object):
    """Interface for uWSGI Caching subsystem."""

    __slots__ = ['name', 'timeout']

    def __init__(self, name=None, timeout=None):
        """
        :param str|unicode name: Cache name with optional address (if @-syntax is used).
        :param int timeout: Expire timeout (seconds). Default 300 (5 minutes).

        """
        self.timeout = timeout or 300
        self.name = name

    def __contains__(self, key):
        """Checks whether there is a value in the cache associated with the given key.

        :param str|unicode key: The cache key to check.

        :rtype: bool
        """
        return uwsgi.cache_exists(key, self.name)

    @property
    def keys(self):
        """Returns a list of keys available in cache.

        :rtype: list

        :raises ValueError: If cache is unavailable.
        """
        return uwsgi.cache_keys(self.name)

    def clear(self):
        """Clears cache the cache."""
        uwsgi.cache_clear(self.name)

    def get(self, key, default=None, as_int=False, setter=None):
        """Gets a value from the cache.

        :param str|unicode key: The cache key to get value for.

        :param default: Value to return if none found in cache.

        :param bool as_int: Return 64bit number instead of str.

        :param callable setter: Setter callable to automatically set cache
            value if not already cached. Required to accept a key and return
            a value that will be cached.

        :rtype: str|unicode|int

        """
        if as_int:
            val = uwsgi.cache_num(key, self.name)
        else:
            val = decode(uwsgi.cache_get(key, self.name))

        if val is None:

            if setter is None:
                return default

            val = setter(key)

            if val is None:
                return default

            self.set(key, val)

        return val

    __getitem__ = get

    def set(self, key, value):
        """Sets the specified key value.

        :param str|unicode key:

        :param int|str|unicode value:

        :rtype: bool
        """
        return uwsgi.cache_set(key, value, self.timeout, self.name)

    __setitem__ = set

    def delete(self, key):
        """Deletes the given cached key from the cache.

        :param str|unicode key: The cache key to delete.

        :rtype: None
        """
        uwsgi.cache_del(key, self.name)

    __delitem__ = delete

    def incr(self, key, delta=1):
        """Increments the specified key value by the specified value.
       
        :param str|unicode key:
    
        :param int delta:

        :rtype: bool
        """
        return uwsgi.cache_inc(key, delta, self.timeout, self.name)

    def decr(self, key, delta=1):
        """Decrements the specified key value by the specified value.

        :param str|unicode key:

        :param int delta:

        :rtype: bool
        """
        return uwsgi.cache_dec(key, delta, self.timeout, self.name)

    def mul(self, key, value=2):
        """Multiplies the specified key value by the specified value.

        :param str|unicode key:

        :param int value:

        :rtype: bool
        """
        return uwsgi.cache_mul(key, value, self.timeout, self.name)

    def div(self, key, value=2):
        """Divides the specified key value by the specified value.

        :param str|unicode key:

        :param int value:

        :rtype: bool
        """
        return uwsgi.cache_mul(key, value, self.timeout, self.name)
