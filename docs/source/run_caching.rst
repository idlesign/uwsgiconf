Caching
=======


.. code-block:: python

    from uwsgiconf.runtime.caching import Cache

    # We'll access preconfigured cache named `mycache`.
    cache = Cache('mycache')

    key_exists = 'mykey' in cache

    def my_setter(key):
        if key == 'anotherkey':
            return 'yes'
        return 'no'

    # Getting cached value and populating it if required in one pass:
    yes_or_no = cache.get('anotherkey', setter=my_setter)



.. automodule:: uwsgiconf.runtime.caching
   :members:
