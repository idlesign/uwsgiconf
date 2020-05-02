from datetime import timedelta
from uwsgiconf.runtime.spooler import Spooler, ResultProcessed, ResultRescheduled, ResultSkipped, spooler_task_types


class FakeUwsgi(object):

    def __init__(self, send_to_spooler=None):
        self.send_func = send_to_spooler

    @property
    def opt(self):
        return {b'spooler': ['/home/here/spooler1', '/home/here/spooler2']}

    def spooler_pids(self):
        return [1, 2]

    def set_spooler_frequency(self, n):
        return n

    def spooler_jobs(self):
        return ['job1', 'job2']

    def spooler_get_task(self, filepath):
        return {'fpath': filepath}

    def send_to_spooler(self, message):

        raw = {
            b'spooler_task_name': b'sometaskname',
        }

        msg = message.get(b'msg')
        if msg:
            raw[b'msg'] = msg

        body = message.get(b'body')
        if body:
            raw[b'body'] = body

        return Spooler._process_message_raw(raw)


def test_spooler_basic(monkeypatch):

    assert spooler_task_types

    monkeypatch.setattr('uwsgiconf.runtime.spooler.uwsgi', FakeUwsgi())

    assert len(Spooler.get_spoolers()) == 2
    assert Spooler.get_pids() == [1, 2]
    assert Spooler.set_period(10) == 10
    assert Spooler.get_tasks() == ['job1', 'job2']
    assert Spooler.read_task_file('filepath') == {'fpath': 'filepath'}

    spooler = Spooler.get_by_basename('spooler2')
    assert isinstance(spooler, Spooler)
    assert str(spooler) == '/home/here/spooler2'

    assert Spooler.send_message_raw('a' * (64 * 1024), spooler=spooler) == ResultProcessed.code_uwsgi


def test_spooler_tasks(monkeypatch):

    faked = FakeUwsgi()
    monkeypatch.setattr('uwsgiconf.runtime.spooler.uwsgi', faked)

    spooler2 = Spooler.get_by_basename('spooler2')

    @Spooler.task(priority=3, postpone=timedelta(seconds=20))
    def spooler1_func(arg1, arg2=10):
        return arg1 + arg2

    @spooler2.task()
    def spooler2_func():
        return 'done'

    @spooler2.task()
    def spooler2_func_fail():
        raise Exception('damn')

    @spooler2.task()
    def spooler2_func_skip():
        return None

    assert spooler1_func(100, 20) == ResultProcessed.code_uwsgi
    assert spooler2_func() == ResultProcessed.code_uwsgi
    assert spooler2_func_skip() == ResultSkipped.code_uwsgi
    assert spooler2_func_fail() == ResultRescheduled.code_uwsgi
