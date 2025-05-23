from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin

from account.models import ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR
from ..models import Service
from common.admin import BaseModelAdmin


@admin.register(Service)
class ServiceAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 50

    list_select_related = ('payout_account', 'organization')

    def get_list_filter(self, request):
        list_filter = ("organization",)
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR):
            list_filter = ()
        return list_filter

    def get_list_display(self, request):
        list_display = ("id", "name", "price", 'category', 'payout_account', "organization", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("name", "price", 'category', 'detail_link')
        elif request.user.role in (ROLE_ACCOUNTANT, ROLE_DOCTOR):
            list_display = ("name", "price", 'category', 'detail_link_view')
        return list_display

    def get_exclude(self, request, obj=None):
        exclude = ()
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT):
            exclude = ('organization',)
        elif request.user.role == ROLE_DOCTOR:
            exclude = ('organization', 'payout_account')
        return exclude

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly = super().get_readonly_fields(request, obj)
        if request.user.role == ROLE_DOCTOR:
            return readonly + ('payout_account_text',)
        return readonly

    def payout_account_text(self, obj):
        return str(obj.payout_account) if obj.payout_account else "-"
    payout_account_text.short_description = "Счёт для выплат"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR):
            return qs.filter(organization=request.user.organization)
        return qs
