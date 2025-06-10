from typing import ClassVar

from django.contrib import admin


class TaskAdmin(admin.ModelAdmin):

    list_display = ("name", "released", "dt_acquired", "dt_released", "dt_created", "dt_updated")
    search_fields = ("name", "owner")
    list_filter: ClassVar = ["released"]
