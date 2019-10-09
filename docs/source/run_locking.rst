Locking
=======

.. code-block:: python

    from uwsgiconf.runtime.locking import lock

    @lock()
    def locked():
        """This function will be locked with default (0) lock."""
        ...

     # or

    with lock(2):
        # Code under this context manager will be locked with lock 2.
        ...




.. automodule:: uwsgiconf.runtime.locking
   :members:
