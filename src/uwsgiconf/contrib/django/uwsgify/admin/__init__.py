from django.contrib import admin

from .models import Configuration, Maintenance, Summary, Workers
from .realms import ConfigurationAdmin, MaintenanceAdmin, SummaryAdmin, WorkersAdmin

admin.site.register(Summary, SummaryAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(Workers, WorkersAdmin)
admin.site.register(Maintenance, MaintenanceAdmin)
