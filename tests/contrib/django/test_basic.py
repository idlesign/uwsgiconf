from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.skip("Live server for development")
def test_run_app(run_app, settings):
    now = timezone.now()

    from uwsgiconf.contrib.django.uwsgify.models import Task
    from uwsgiconf.runtime.mules import Farm
    from uwsgiconf.runtime.scheduling import register_cron

    farm = Farm('farm1')

    @register_cron(target=farm)
    def task_null_acq():
        print("task_null_acq")

    @register_cron(target=farm)
    def task_null_rel():
        """Some description.

        Multiline.
        """
        print("task_null_rel")

    def get_time(hour: int):
        return now.replace(hour=hour, minute=30, second=0, microsecond=0)

    Task.register("task_acq_lt_rel", dt_acquired=get_time(11), dt_released=get_time(12))
    Task.register("task_acq_gt_rel", dt_acquired=now-timedelta(hours=1), dt_released=now-timedelta(hours=8))
    Task.register("task_null_acq", dt_acquired=None, dt_released=get_time(11))
    Task.register("task_null_rel", dt_acquired=get_time(10), dt_released=None)

    run_app()
