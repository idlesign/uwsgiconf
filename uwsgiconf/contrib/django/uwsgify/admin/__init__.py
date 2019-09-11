from django.contrib import admin

from .models import Summary, Configuration
from .realms import SummaryAdmin, ConfigurationAdmin

admin.site.register(Summary, SummaryAdmin)
admin.site.register(Configuration, ConfigurationAdmin)
