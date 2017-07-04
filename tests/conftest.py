import pytest


@pytest.fixture(scope='session')
def ini():

    def wrapped(section):
        return section.as_configuration().format()

    return wrapped


@pytest.fixture(scope='session')
def assert_lines(ini):

    def wrapped(lines, source, assert_in=True):
        source = ini(source)

        if not isinstance(lines, list):
            lines = [lines]

        for line in lines:
            if assert_in:
                assert line in source
            else:
                assert line not in source

    return wrapped
