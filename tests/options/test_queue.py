from uwsgiconf.config import Section


def test_queue_basics(assert_lines):

    assert_lines([
        'queue = 100',
        'queue-blocksize = 131072',
    ], Section().queue.enable(100, block_size=131072))
