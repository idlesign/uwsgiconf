from uwsgiconf.runtime.rpc import *


def test_rpc():

    @register_rpc()
    def expose_me():
        pass

    make_rpc_call('expose_me')
    make_rpc_call('remotefunc', remote='@faraway')

    get_rpc_list()
