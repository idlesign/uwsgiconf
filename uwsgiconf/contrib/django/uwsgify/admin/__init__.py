from django.contrib import admin

from .models import Summary, Configuration, Workers
from .realms import SummaryAdmin, ConfigurationAdmin, WorkersAdmin

admin.site.register(Summary, SummaryAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(Workers, WorkersAdmin)
