from uwsgiconf.runtime.monitoring import *


def test_metric():

    m = Metric('mycounter')

    value = m.value

    m.set(10)
    m.set(20, mode='min')
    m.set(5, mode='max')

    m.incr()
    m.decr()
    m.mul()
    m.div()


def test_file_monitor():

    @register_file_monitor('/here/there.file')
    def handle_file_modification(sig_num):
        pass
