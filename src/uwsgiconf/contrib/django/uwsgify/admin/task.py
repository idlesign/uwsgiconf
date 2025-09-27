from typing import ClassVar

from django.contrib import admin, messages
from django.db.models import QuerySet, TextField
from django.forms import Textarea
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from uwsgiconf.runtime.signals import REGISTERED_SIGNALS, Signal

from ..utils import LOGGER


class TaskAdmin(admin.ModelAdmin):

    list_display = ('name', 'active', 'released', 'duration', 'dt_acquired', 'dt_released', 'dt_updated')
    search_fields = ('name', 'owner')
    list_filter: ClassVar = ['active', 'released']
    ordering: ClassVar = ['name']
    readonly_fields = ('duration', 'dt_updated', 'dt_created')

    fieldsets = (
        (_('Basic'), {
            'fields': ('name', 'active', 'released', 'duration'),
        }),
        (_('Date and time'), {
            'fields': ('dt_created', 'dt_updated', 'dt_acquired', 'dt_released'),
        }),
        (_('Context'), {
            'fields': ('owner', 'params', 'result'),
        }),
    )

    formfield_overrides: ClassVar = {
        TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }

    actions: ClassVar = [
        'run_now',
    ]

    @admin.action(description=_('Run now'))
    def run_now(self, request: HttpRequest, queryset: QuerySet):
        names = set(queryset.values_list('name', flat=True))
        known_tasks = {sig.func.__name__: sig for sig in REGISTERED_SIGNALS.values()}
        tasks_set = set(known_tasks)
        tasks_known = tasks_set.intersection(names)
        run = []

        for func_name in tasks_known:
            sig = known_tasks[func_name]
            LOGGER.info(f'Force run task. Send signal {sig.num} for task {func_name}')
            run.append(func_name)
            Signal(sig.num).send()

        if run:
            messages.info(request, _('Running: %s.') % ', '.join(sorted(run)))

        if missing := tasks_set.symmetric_difference(names):
            messages.error(request, _('Unable to run tasks unregistered with uWSGI: %s.') % ', '.join(sorted(missing)))
