from uwsgiconf.runtime.mules import *


def test_mule():

    current = Mule.get_current_id()

    mule = Mule(1)
    mule.send('ping')
    msg = mule.get_message()


def test_farm():

    current = Mule.get_current_id()

    farm = Farm('first')

    assert not farm.is_mine

    farm.send('ping')
    msg = farm.get_message()
