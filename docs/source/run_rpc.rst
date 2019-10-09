RPC
===

.. code-block:: python

    from uwsgiconf.runtime.rpc import register_rpc, make_rpc_call, get_rpc_list

    @register_rpc()
    def expose_me(arg1, arg2=15):
        print('RPC called %s' % arg1)

    make_rpc_call('expose_me', ['value1'])

    all_rpc = get_rpc_list()  # Registered RPC items list.



.. automodule:: uwsgiconf.runtime.rpc
   :members:
