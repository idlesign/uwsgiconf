from typing import ClassVar

from django.contrib import admin, messages
from django.db.models import QuerySet, TextField
from django.forms import Textarea
from django.http import HttpRequest
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from uwsgiconf.runtime.signals import REGISTERED_SIGNALS, Signal, SignalDescription

from ..models import Task
from ..utils import LOGGER


class TaskAdmin(admin.ModelAdmin):

    list_display = ('name', 'active', 'released', 'duration', 'dt_acquired', 'dt_released', 'dt_updated')
    search_fields = ('name', 'owner')
    list_filter: ClassVar = ['active', 'released']
    ordering: ClassVar = ['name']
    readonly_fields = ('duration', 'info', 'dt_updated', 'dt_created')

    fieldsets = (
        (_('Basic'), {
            'fields': ('name', 'info', 'active', 'released', 'duration'),
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

    @property
    def known_tasks(self) -> dict[str, SignalDescription]:
        return {sig.func.__name__: sig for sig in REGISTERED_SIGNALS.values()}

    @admin.action(description=_('Run now'))
    def run_now(self, request: HttpRequest, queryset: QuerySet):
        names = set(queryset.values_list('name', flat=True))
        known_tasks = self.known_tasks
        run = []
        missing = []

        for func_name in names:
            if sig := known_tasks.get(func_name):
                LOGGER.info(f'Force run task. Send signal {sig.num} for task {func_name}')
                run.append(func_name)
                Signal(sig.num).send()
            else:
                missing.append(func_name)

        if run:
            messages.info(request, _('Running: %s.') % ', '.join(sorted(run)))

        if missing:
            messages.error(request, _('Unable to run tasks unregistered with uWSGI: %s.') % ', '.join(sorted(missing)))

    def info(self, task: Task):
        text = ""

        if task_info := self.known_tasks.get(task.name):
            text = '<div>' + '</div><div>'.join(
                f'• <b>{key}:</b> {escape(value)}'
                for key, value in {
                    _('Description'): task_info.func.__doc__,
                    _('Parameters'): f'{getattr(task_info.func, "params_hint", None)}',
                    _('Target'): task_info.target,
                    _('Signal'): task_info.num,
                    _('Function'): task_info.func,
                }.items()
            ) + '</div>'

        elif task.pk:
            text = '<div class="info"><b>{text}</b></div>'.format(
                text=_('No information available. Task with this name is not registered within uWSGI.')
            )

        return mark_safe(text)

    info.short_description = _('Info')
