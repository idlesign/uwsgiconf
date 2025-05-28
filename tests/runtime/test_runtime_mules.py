from uwsgiconf.runtime.mules import Farm, Mule


def test_mule(monkeypatch):

    assert not Mule.get_message()

    current_mule = Mule.get_current()
    assert current_mule is None

    monkeypatch.setattr('uwsgiconf.runtime.mules.Mule.get_current_id', lambda *args: 1)
    current_mule = Mule.get_current()
    assert f"{current_mule}" == '1'
    assert current_mule.send('some')

    result = []

    @current_mule.offload()
    def offloaded(add):
        result.append(add)

    offloaded(2)
    assert result == [2]


def test_farm(monkeypatch):

    monkeypatch.setattr('uwsgiconf.runtime.mules.uwsgi.opt', {b'farm': b'myfarm:1,2,3'})

    farms = Farm.get_farms()
    assert len(farms) == 1

    farm = farms[0]
    assert str(farm) == 'myfarm: 1, 2, 3'
    assert not farm.is_mine

    farm.send('ping')
    assert not farm.get_message()

    result = []

    @farm.offload()
    def offloaded():
        result.append(44)

    offloaded()
    assert result == [44]
