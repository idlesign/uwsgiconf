import pytest

from uwsgiconf.exceptions import ConfigurationError
from uwsgiconf.options.routing_modifiers import ModifierCache


def test_routing_modifiers():

    with pytest.raises(ConfigurationError):
        ModifierCache(44)
