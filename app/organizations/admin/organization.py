from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from account.models import ROLE_ADMIN
from ..models import Organization
from common.admin import BaseModelAdmin


@admin.register(Organization)
class OrganizationAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    ordering = ("name",)

    def get_search_fields(self, request):
        search_fields = ("name", "address", "phone_number", "email")
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            search_fields = ()
        return search_fields

    def get_list_filter(self, request):
        list_filter = ("address",)
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_filter = ()
        return list_filter

    def get_list_display(self, request):
        list_display = ("id", "name", "address", "phone_number", "email", "website", "logo", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("name", "address", "phone_number", "email", "website", "logo", 'detail_link')
        return list_display

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(id=request.user.organization_id)