from django.contrib import admin

from account.models import ROLE_ADMIN
from ..models import Room, Building
from common.admin import BaseModelAdmin


@admin.register(Room)
class RoomAdmin(BaseModelAdmin):
    search_fields = ("room_number", "building__name",)
    list_filter = ("building", "floor")
    ordering = ("room_number",)
    autocomplete_fields = ("services",)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == ROLE_ADMIN:
            organization = request.user.organization
            if db_field.name == "building":
                kwargs["queryset"] = Building.objects.filter(organization=organization)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_list_display(self, request):
        list_display = ("id", "room_number", "floor", "building", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("room_number", "floor", "building", 'detail_link')
        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(building__organization=request.user.organization)
