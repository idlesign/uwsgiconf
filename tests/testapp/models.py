from uwsgiconf.contrib.django.uwsgify.models import TaskBase


class Task(TaskBase):
    """Inherited concrete."""

    class Meta:
        app_label = "testapp"
