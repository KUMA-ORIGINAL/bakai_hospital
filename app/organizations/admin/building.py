from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from account.models import ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR
from common.admin import BaseModelAdmin
from organizations.models import Building


@admin.register(Building)
class BuildingAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    search_fields = ("name", "address", "organization__name")
    ordering = ("name",)

    def get_list_filter(self, request):
        list_filter = ("organization",)
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_filter = ()
        return list_filter

    def get_list_display(self, request):
        list_display = ("id", "name", "address", "organization", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("name", "address", 'detail_link')
        return list_display

    def get_exclude(self, request, obj=None):
        exclude = ()
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            exclude = ('organization',)
        return exclude

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR):
            return qs.filter(organization=request.user.organization)