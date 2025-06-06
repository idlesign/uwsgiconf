from tests.testapp.models import Task


def test_basic():
    assert Task.acquire("some") is None
