import pytest


from uwsgiconf.options.routing_modifiers import ModifierCache
from uwsgiconf.exceptions import ConfigurationError


def test_routing_modifiers():

    with pytest.raises(ConfigurationError):
        ModifierCache(44)
