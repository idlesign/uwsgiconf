Configuration [Dynamic]
=======================


**uwsgiconf** comes with ``runtime`` package which is similar to **uwsgidecorators** but offers different
abstractions to provide useful shortcuts and defaults.

Various modules from that package can be imported and used runtime to configure different aspects of **uWSGI**,
such as `caching`, `locks`, `signals`, `spooler`, `rpc`, etc.

Below are just a few examples of how you can use ``runtime`` configuration.


Cache
-------

.. warning:: To use this helper one needs to configure cache(s) in uWSGI config beforehand.

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



Control
-------

.. code-block:: python

    from uwsgiconf.runtime.control import harakiri_imposed, reload

    @harakiri_imposed(1)
    def doomed():
        """Master process will kill this function after 1 sec."""

    # or

    with harakiri_imposed(30):
        # Master will kill worker if code under that manager won't finish in 30 sec.

    # We'll reload uWSGI.
    reload()


Locks
-----

.. code-block:: python

    from uwsgiconf.runtime.locking import lock

    @lock()
    def locked():
        """This function will be locked with default (0) lock."""

     # or

    with lock(2):
        # Code under this context manager will be locked with lock 2.




Mules
-----

.. code-block:: python

    from uwsgiconf.runtime.mules import Mule, Farm

    first_mule = Mule(1)

    @first_mule.offload()
    def for_mule(*args, **kwargs):
        # This function will be offloaded to and handled by mule 1.
        ...

    farm_two = Farm('two')

    @farm_two.offload()
    def for_farm(*args, **kwargs):
        # And this one will be offloaded to farm `two` and handled by any mule from that farm.
        ...


RPC
---

.. code-block:: python

    from uwsgiconf.runtime.rpc import register_rpc, make_rpc_call, get_rpc_list

    @register_rpc()
    def expose_me(arg1, arg2=15):
        print('RPC called %s' % arg1)

    make_rpc_call('expose_me', ['value1'])

    all_rpc = get_rpc_list()  # Registered RPC items list.


Scheduling
----------

.. code-block:: python

    from uwsgiconf.runtime.scheduling import register_timer_rb, register_cron

    @register_timer_rb(10, repeat=2)
    def repeat_twice():
        """This function will be called twice with 10 seconds interval
        (by default in in first available mule) using red-black tree based timer.

        """

    @register_cron(day=-3, hour='10-18/2')
    def do_something():
        """This will be run every 3rd day, from 10 till 18 every 2 hours."""


Spooler
-------

.. warning:: To use this helper one needs to configure spooler(s) in uWSGI config beforehand.

.. code-block:: python

    my_spooler = Spooler.get_by_basename('myspooler')

    # @Spooler.task() to  run on first available or to run on `my_spooler`:
    @my_spooler.task(postpone=timedelta(seconds=1))
    def run_me(a, b='c'):
        # We do:
        # * return True if task processed
        # * return None if task was ignored
        # * raise an exception to force task retry
        return True

    # Now call this function as usual and it'll run in a spooler.
    ...
    run_me('some', b='other')
    ...

