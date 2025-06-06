from datetime import timedelta
from socket import gethostname
from typing import Optional

from django.db import models
from django.db.transaction import atomic
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from uwsgiconf.contrib.django.uwsgify.utils import LOGGER


class TaskBase(models.Model):
    """Base model for a distributed task.

    This allows to run only one instance of the task no matter
    how many application instances (in various datacenters) we have.

    It also features task parametrization and result store.

    """

    STALE_TIMEOUT = 1800  # 30 minutes
    """Timeout (seconds) to consider the task stale (hung up)."""

    dt_created = models.DateTimeField(verbose_name=_('Created at'), blank=True, auto_now_add=True, db_column='dt_add')
    dt_updated = models.DateTimeField(verbose_name=_('Updated at'), blank=True, auto_now=True, db_column='dt_upd')

    name = models.TextField(verbose_name=_('Name'), unique=True)
    owner = models.TextField(verbose_name=_('Owner'), blank=True, default='')
    
    released = models.BooleanField(verbose_name=_('Released'), blank=True, default=True, db_index=True)

    dt_acquired = models.DateTimeField(verbose_name=_('Acquired at'), blank=True, null=True, db_column='dt_acc')
    dt_released = models.DateTimeField(verbose_name=_('Released at'), blank=True, null=True, db_column='dt_rel')

    params = models.JSONField(verbose_name=_('Parameters'), blank=True, default=dict)
    result = models.JSONField(verbose_name=_('Result'), blank=True, default=dict, help_text='The previous run result.')

    class Meta:
        abstract = True
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __str__(self) -> str:
        return self.name

    def get_owner(self) -> str:
        """Returns the "owner" for this task."""
        return gethostname()

    @classmethod
    def acquire(cls, name: str) -> Optional['TaskBase']:
        """Tries to acquire the task. Returns `None` on fail
        (e.g. the task has already been acquired).

        :param name: Task name
        """
        with atomic():
            acquired: TaskBase = cls.objects.select_for_update(
                skip_locked=True
            ).filter(name=name, released=True).first()

            if acquired:
                LOGGER.debug('Lock is acquired: %s', name)
                acquired.released = False
                acquired.dt_acquired = now()
                acquired.owner = acquired.get_owner()
                acquired.save()

            else:
                LOGGER.debug('Lock is NOT acquired: %s', name)

        return acquired

    def release(self, result: dict | None = None):
        """Releases the task, thus making it available for another acquirement.
        Use `None` to keep an existing result.

        :param result: Result to store.
        """
        self.released = True
        self.dt_released = now()

        if result is not None:
            self.result = result

        self.save()

    @classmethod
    def cleanup_stale(cls):
        """Resets stale (hung up) tasks records, thus making them available
        for further acquirement."""
        LOGGER.debug('Cleanup stale tasks for "%s"', cls.__name__)

        cls.objects.filter(
            released=False,
            update_dt__lte=now() - timedelta(seconds=cls.STALE_TIMEOUT)
        ).update(released=True)
