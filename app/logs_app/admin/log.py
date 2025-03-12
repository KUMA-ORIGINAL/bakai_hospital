from django.contrib import admin
from import_export.admin import ExportActionModelAdmin
from unfold.contrib.import_export.forms import ExportForm

from ..models import Log
from common.admin import BaseModelAdmin


@admin.register(Log)
class LogAdmin(BaseModelAdmin, ExportActionModelAdmin):
    list_display = ("id", "action", "entity", "entity_id", "user_id", "user_type", "created_at", "organization")
    search_fields = ("entity", "user_id", "organization__name")
    list_filter = ("action", "user_type", "organization")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

    export_form_class = ExportForm

    fieldsets = (
        (None, {
            "fields": ("action", "entity", "entity_id", "user_id", "user_type", "details", "old_data", "organization")
        }),
        ('Дополнительная информация', {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
