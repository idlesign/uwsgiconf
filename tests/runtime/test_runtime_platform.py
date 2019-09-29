from uwsgiconf.runtime.platform import uwsgi


def test_platform_stub():

    assert not uwsgi.worker_id
    assert not uwsgi.workers_info
    assert not uwsgi.ready_for_requests
    assert uwsgi.memory == (0, 0)
    assert not uwsgi.clock
    assert not uwsgi.get_listen_queue()
    assert uwsgi.get_version() == '0.0.0'
    assert uwsgi.get_version(as_tuple=True) == (0, 0, 0, 0, '')
    assert uwsgi.master_pid == -1
    assert uwsgi.config_variables == {}
    assert uwsgi.config == {}
    assert uwsgi.hostname == ''

    hooked = []

    @uwsgi.postfork_hooks.add()
    def hookit():
        hooked.append('yes')
        return True

    uwsgi.postfork_hooks.run()
    assert len(hooked) == 1
    assert hooked[0] == 'yes'
