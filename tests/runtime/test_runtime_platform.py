from uwsgiconf.runtime.platform import uwsgi


def test_platform_stub():

    assert not uwsgi.worker_id
    assert not uwsgi.workers_info
    assert not uwsgi.ready_for_requests
    assert uwsgi.memory == (0, 0)
    assert not uwsgi.clock
    assert not uwsgi.get_listen_queue()
    assert uwsgi.get_version() == '0.0.0'
