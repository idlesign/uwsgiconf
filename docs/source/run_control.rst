Control
=======

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


.. automodule:: uwsgiconf.runtime.control
   :members:
