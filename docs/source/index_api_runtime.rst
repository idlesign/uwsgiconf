Configuration [Dynamic]
=======================


**uwsgiconf** comes with ``runtime`` package which is similar to **uwsgidecorators** but offers different abstractions.

Various modules from that package can be imported and used runtime to configure different aspects of **uWSGI**,
such as *caching*, *locks*, *signals*, *rpc*, etc.

Below are some examples of how you can use ``runtime`` configuration.


Control
-------

.. code-block:: python

    from uwsgiconf.runtime.control import harakiri_imposed

    @harakiri_imposed(1)
    def doomed():
        """Master process will kill this function after 1 sec."""

    # or

    with harakiri_imposed(30):
        # Master will kill worker if code under that manager won't finish in 30 sec.



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




Scheduling
----------

.. code-block:: python

    from uwsgiconf.runtime.scheduling import register_timer_rb

    @register_timer_rb(10, repeat=2)
    def repeat_twice():
        """This function will be called twice with 10 seconds interval
        (by default in in first available mule) using red-black tree based timer.

        """
