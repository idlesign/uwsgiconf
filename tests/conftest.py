import pytest


@pytest.fixture(scope='session')
def ini():

    def wrapped(section, stamp):
        return section.as_configuration().format(stamp=stamp)

    return wrapped


@pytest.fixture(scope='session')
def assert_lines(ini):

    def wrapped(lines, source, assert_in=True, stamp=False):
        source = ini(source, stamp)

        if not isinstance(lines, list):
            lines = [lines]

        for line in lines:
            if assert_in:
                assert line in source
            else:
                assert line not in source

    return wrapped
