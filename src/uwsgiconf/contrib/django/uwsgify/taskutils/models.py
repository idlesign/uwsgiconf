from datetime import timedelta
from socket import gethostname
from typing import Optional

from django.contrib import admin
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

    active = models.BooleanField(verbose_name=_("Active"), blank=True, default=True)

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

    def _get_owner(self) -> str:
        """Returns "owner" (executor) for this task."""
        return gethostname()

    @classmethod
    def _get_manager(cls) -> models.Manager:
        """Returns model manager."""
        return cls.objects

    @classmethod
    def register(cls, name: str, *, params: dict | None = None, **kwargs) -> 'TaskBase':
        """Register a new task."""
        return cls._get_manager().create(name=name, params=params or {}, **kwargs)

    @classmethod
    def acquire(cls, name: str, **kwargs) -> Optional['TaskBase']:
        """Tries to acquire the task. Returns `None` on fail
        (e.g. the task has already been acquired).

        :param name: Task name
        """
        with atomic():
            kwargs = {'active': True, **kwargs}
            acquired: TaskBase = cls._get_manager().select_for_update(
                skip_locked=True
            ).filter(name=name, released=True, **kwargs).first()

            if acquired:
                LOGGER.debug('Task lock is acquired: %s', name)
                acquired.released = False
                acquired.dt_acquired = now()
                acquired.owner = acquired._get_owner()
                acquired.save()

            else:
                LOGGER.debug('Task lock is NOT acquired: %s', name)

        return acquired

    @property
    @admin.display(description=_('Duration'))
    def duration(self) -> timedelta:
        """Returns the duration of the task as a timedelta."""
        result = timedelta()

        if (dt_acquired := self.dt_acquired) and (dt_released := self.dt_released):
            if dt_acquired > dt_released:
                # still running
                result = now() - dt_acquired
            else:
                result = dt_released - dt_acquired

        result = timedelta(seconds=int(result.total_seconds()))

        return result

    def release(self, *, result: dict | None = None):
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
    def reset_stale(cls, *, timeout: int = STALE_TIMEOUT):
        """Resets stale (hung up) tasks records, thus making them available
        for further acquirement.

        :param timeout: Timeout (seconds) to consider the task stale (hung up).
        """
        LOGGER.debug('Cleanup stale tasks for "%s"', cls.__name__)

        cls._get_manager().filter(
            released=False,
            dt_updated__lte=now() - timedelta(seconds=timeout)
        ).update(released=True)
