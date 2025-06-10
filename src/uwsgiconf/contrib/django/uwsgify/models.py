from django.utils.translation import gettext_lazy as _

from .taskutils.models import TaskBase


class Task(TaskBase):
    """Builtin default task model."""

    class Meta:
        db_table = 'uwsgify_tasks'
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
