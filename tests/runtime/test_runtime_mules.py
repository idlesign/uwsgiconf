from uwsgiconf.runtime.mules import Mule, Farm, _mule_messages_hook


def test_mule(monkeypatch):

    assert not Mule.get_message()

    current_mule = Mule.get_current()
    assert current_mule is None

    monkeypatch.setattr('uwsgiconf.runtime.mules.Mule.get_current_id', lambda *args: 1)
    current_mule = Mule.get_current()
    assert str(current_mule) == '1'
    current_mule.send('some')

    @current_mule.offload()
    def offloaded(add):
        return 33 + add

    def fake_send(self, message):
        assert self.id is current_mule.id
        return _mule_messages_hook(message)

    monkeypatch.setattr('uwsgiconf.runtime.mules.Mule.send', fake_send)

    assert offloaded(2) == 35


def test_farm(monkeypatch):

    monkeypatch.setattr('uwsgiconf.runtime.mules.uwsgi.opt', {b'farm': b'myfarm:1,2,3'})

    farms = Farm.get_farms()
    assert len(farms) == 1

    farm = farms[0]
    assert str(farm) == 'myfarm: 1, 2, 3'
    assert not farm.is_mine

    farm.send('ping')
    assert not farm.get_message()

    @farm.offload()
    def offloaded():
        return 44
