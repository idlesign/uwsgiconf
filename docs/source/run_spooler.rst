Spooler
=======


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



.. automodule:: uwsgiconf.runtime.spooler
   :members:
