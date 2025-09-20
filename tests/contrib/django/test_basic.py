import pytest


@pytest.mark.skip("Live server for development")
def test_run_app(run_app):
    run_app()
