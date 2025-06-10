from django.contrib import admin

from ..models import Task
from .models import Configuration, Maintenance, Summary, Workers
from .realms import ConfigurationAdmin, MaintenanceAdmin, SummaryAdmin, WorkersAdmin
from .task import TaskAdmin

admin.site.register(Summary, SummaryAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(Workers, WorkersAdmin)
admin.site.register(Maintenance, MaintenanceAdmin)
admin.site.register(Task, TaskAdmin)
