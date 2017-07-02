import pytest


@pytest.fixture(scope='session')
def ini():

    def wrapped(section):
        return section.as_configuration().format()

    return wrapped


@pytest.fixture(scope='session')
def assert_lines(ini):

    def wrapped(lines, source):
        source = ini(source)

        if not isinstance(lines, list):
            lines = [lines]

        for line in lines:
            assert line in source

    return wrapped
