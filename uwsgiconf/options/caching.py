from ..base import OptionsGroup
from ..utils import KeyValue


class Caching(OptionsGroup):
    """Caching.

    uWSGI includes a very fast, all-in-memory, zero-IPC, SMP-safe, constantly-optimizing,
    highly-tunable, key-value store simply called "the caching framework".

    A single uWSGI instance can create an unlimited number of "caches" each one
    with different setup and purpose.

    * http://uwsgi-docs.readthedocs.io/en/latest/Caching.html
    * http://uwsgi-docs.readthedocs.io/en/latest/tutorials/CachingCookbook.html

    """

    def set_basic_params(self, no_expire=None, expire_scan_interval=None, report_freed=None):
        """
        :param bool no_expire: Disable auto sweep of expired items.
            Since uWSGI 1.2, cache item expiration is managed by a thread in the master process,
            to reduce the risk of deadlock. This thread can be disabled
            (making item expiry a no-op) with the this option.

        :param int expire_scan_interval: Set the frequency (in seconds) of cache sweeper scans. Default: 3.

        :param bool report_freed: Constantly report the cache item freed by the sweeper.

            .. warning:: Use only for debug.

        """
        self._set('cache-no-expire', no_expire, cast=bool)
        self._set('cache-report-freed-items', report_freed, cast=bool)
        self._set('cache-expire-freq', expire_scan_interval)

        return self._section

    def add_item(self, key, value, cache_name=None):
        """Add an item into the given cache.

        This is a commodity option (mainly useful for testing) allowing you
        to store an item in a uWSGI cache during startup.

        :param str|unicode key:

        :param value:

        :param str|unicode cache_name: If not set, default will be used.

        """
        cache_name = cache_name or ''
        value = '%s %s=%s' % (cache_name, key, value)

        self._set('add-cache-item', value.strip(), multi=True)

        return self._section

    def add_file(self, filepath, gzip=False, cache_name=None):
        """Load a static file in the cache.

        .. note:: Items are stored with the filepath as is (relative or absolute) as the key.

        :param str|unicode filepath:

        :param bool gzip: Use gzip compression.

        :param str|unicode cache_name: If not set, default will be used.

        """
        command = 'load-file-in-cache'

        if gzip:
            command += '-gzip'

        cache_name = cache_name or ''
        value = '%s %s' % (cache_name, filepath)

        self._set(command, value.strip(), multi=True)

        return self._section

    def add_cache(
            self, name, max_items, expires=None, store=None, store_sync_interval=None, store_delete=None,
            hash_algo=None, hash_size=None, key_size=None, udp_clients=None, udp_servers=None,
            block_size=None, block_count=None, sync_from=None, mode_bitmap=None, use_lastmod=None,
            full_silent=None, full_purge_lru=None):
        """Creates cache. Default mode: single block.

        .. note:: This uses new generation ``cache2`` option available since uWSGI 1.9.

        .. note:: When at least one cache is configured without ``full_purge_lru``
            and the master is enabled a thread named "the cache sweeper" is started.
            Its main purpose is deleting expired keys from the cache.
            If you want auto-expiring you need to enable the master.

        :param str|unicode name: Set the name of the cache. Must be unique in an instance.

        :param int max_items: Set the maximum number of cache items.

            .. note:: Effective number of items is **max_items - 1** -
                the first item of the cache is always internally used as "NULL/None/undef".

        :param int expires: The number of seconds after the object is no more valid
            (and will be removed by the cache sweeper when ``full_purge_lru`` is not set.

        :param str|unicode store: Set the filename for the persistent storage.
            If it doesn't exist, the system assumes an empty cache and the file will be created.

        :param int store_sync_interval: Set the number of seconds after which msync() is called
            to flush memory cache on disk when in persistent mode.
            By default it is disabled leaving the decision-making to the kernel.

        :param bool store_delete: uWSGI, by default, will not start if a cache file exists
            and the store file does not match the configured items/blocksize.
            Setting this option will make uWSGI delete the existing file upon mismatch
            and create a new one.

        :param str|unicode hash_algo: Set the hash algorithm used in the hash table. Current options are:

            * djb33x (default)
            * murmur2

        :param int hash_size: This is the size of the hash table in bytes.
            Generally 65536 (the default) is a good value.

            .. note:: Change it only if you know what you are doing
                or if you have a lot of collisions in your cache.

        :param int key_size: Set the maximum size of a key, in bytes. Default: 2048.

        :param str|unicode|list udp_clients: List of UDP servers which will receive UDP cache updates.

        :param str|unicode |list udp_servers: List of UDP addresses on which to bind the cache
            to wait for UDP updates.

        :param int block_size: Set the size (in bytes) of a single block.

            .. note:: It's a good idea to use a multiple of 4096 (common memory page size).

        :param int block_count: Set the number of blocks in the cache. Useful only in bitmap mode,
            otherwise the number of blocks is equal to the maximum number of items.

        :param str|unicode|list sync_from: List of uWSGI addresses which the cache subsystem will connect to
            for getting a full dump of the cache. It can be used for initial cache synchronization.
            The first node sending a valid dump will stop the procedure.
            
        :param bool mode_bitmap: Enable (more versatile but relatively slower) bitmap mode.

            http://uwsgi-docs.readthedocs.io/en/latest/Caching.html#single-block-faster-vs-bitmaps-slower

            .. warning:: Considered production ready only from uWSGI 2.0.2.

        :param bool use_lastmod: Enabling will update last_modified_at timestamp of each cache
            on every cache item modification. Enable it if you want to track this value
            or if other features depend on it. This value will then be accessible via the stats socket.

        :param bool full_silent: By default uWSGI will print warning message on every cache set operation
            if the cache is full. To disable this warning set this option.

            .. note:: Available since 2.0.4.

        :param bool full_purge_lru: Allows the caching framework to evict Least Recently Used (LRU)
            item when you try to add new item to cache storage that is full.

            .. note:: ``expires`` argument will be ignored.

        """
        value = KeyValue(
            locals(),
            keys=[
                'name', 'max_items', 'expires', 'store', 'store_sync_interval', 'store_delete',
                'hash_algo', 'hash_size', 'key_size', 'udp_clients', 'udp_servers',
                'block_size', 'block_count', 'sync_from', 'mode_bitmap', 'use_lastmod',
                'full_silent', 'full_purge_lru',
            ],
            aliases={
                'max_items': 'maxitems',
                'store_sync_interval': 'storesync',
                'hash_algo': 'hash',
                'udp_clients': 'nodes',
                'block_size': 'blocksize',
                'block_count': 'blocks',
                'sync_from': 'sync',
                'mode_bitmap': 'bitmap',
                'use_lastmod': 'lastmod',
                'full_silent': 'ignore_full',
                'full_purge_lru': 'purge_lru',
            },
            bool_keys=['store_delete', 'mode_bitmap', 'use_lastmod', 'full_silent', 'full_purge_lru'],
            list_keys=['udp_clients', 'udp_servers', 'sync_from'],
        )

        self._set('cache2', value, multi=True)

        return self._section
