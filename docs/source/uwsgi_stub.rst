Python uwsgi module stub
========================

**uwsgiconf** comes with documented **uwsgi** module that you can import instead of ``import uwsgi``.

.. code-block:: python

    # Instead of
    import uwsgi

    # you can do.
    from uwsgiconf import uwsgi


That way **uwsgi** will be available runtime as usual, besides you will get autocompletion
and hints in IDE, and won't get ``ImportError`` when run without **uwsgi**.

This also will facilitate your testing a bit, for those simple cases when you won't expect any result from **uwsgi** function.


.. warning:: This is a stub module, so it doesn't really implement functions defined in it.
   Use it for documentation purposes.


.. automodule:: uwsgiconf.uwsgi_stub
   :members:
