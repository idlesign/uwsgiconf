Platform
========

Platform object is available in ``uwsgi`` module attribute:


.. code-block:: python

    from uwsgiconf.runtime.platform import uwsgi

    rss, vsz = uwsgi.memory

    print(uwsgi.config)

    @uwsgi.postfork_hooks.add()
    def db_close_connections():
        """This will be called after fork()."""
        print('Forked!')


.. autoclass:: uwsgiconf.runtime.platform._Platform
   :members:


.. autoclass:: uwsgiconf.runtime.request._Request
   :members:
