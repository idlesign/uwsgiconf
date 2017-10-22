from uwsgiconf.runtime.locking import *


def test_locking():

    @lock()
    def locked():
        pass

    locked()

    with lock():
        pass

    my_lock = lock(10)

    assert int(my_lock) == 10
    assert not my_lock.is_set
