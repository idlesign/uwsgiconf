from uwsgiconf.runtime.rpc import register_rpc, make_rpc_call, get_rpc_list


def test_rpc():

    results = []

    @register_rpc()
    def remotefunc():
        results.append('remotefunc')

    @register_rpc()
    def expose_me(a, b):
        results.append(f'expose_me {a}, {b}')

    make_rpc_call('expose_me', args=['1', '2'])
    make_rpc_call('remotefunc', remote='@faraway')

    assert results == ["expose_me b'1', b'2'", 'remotefunc']

    assert get_rpc_list() == ('remotefunc', 'expose_me')
