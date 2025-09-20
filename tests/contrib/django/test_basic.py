from datetime import timedelta

import pytest
from django.utils import timezone

from uwsgiconf.contrib.django.uwsgify.models import Task


@pytest.mark.skip("Live server for development")
def test_run_app(run_app):
    now = timezone.now()
    Task.register("task_1", dt_acquired=now-timedelta(hours=2), dt_released=now-timedelta(minutes=35))
    run_app()
