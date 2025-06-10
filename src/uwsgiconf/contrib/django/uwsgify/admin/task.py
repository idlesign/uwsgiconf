from typing import ClassVar

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from uwsgiconf.runtime.signals import REGISTERED_SIGNALS, Signal

from ..utils import LOGGER


class TaskAdmin(admin.ModelAdmin):

    list_display = ('name', 'released', 'dt_acquired', 'dt_released', 'dt_created', 'dt_updated')
    search_fields = ('name', 'owner')
    list_filter: ClassVar = ['released']

    actions: ClassVar = [
        'run_now',
    ]

    @admin.action(description=_('Run now'))
    def run_now(self, request: HttpRequest, queryset: QuerySet):
        names = set(queryset.values_list('name', flat=True))
        run = []

        for sig in REGISTERED_SIGNALS.values():
            func_name = sig.func.__name__
            if func_name in names:
                LOGGER.debug(f'Force run task. Send signal {sig.num} for task {func_name}')
                run.append(func_name)
                Signal(sig.num).send()

        if run:
            messages.info(request, _('Running: %s.') % ', '.join(sorted(run)))
