Scheduling
==========

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



.. automodule:: uwsgiconf.runtime.scheduling
   :members:
