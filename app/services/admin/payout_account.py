from django.contrib import admin
from account.models import ROLE_ADMIN
from ..models import PayoutAccount
from common.admin import BaseModelAdmin


@admin.register(PayoutAccount)
class PayoutAccountAdmin(BaseModelAdmin):
    list_display = ("id", "name", "provider", "organization")
    search_fields = ("name", "provider", "organization__name")
    ordering = ("name",)
    list_per_page = 50

    def get_list_filter(self, request):
        list_filter = ("provider", "organization")
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_filter = ("provider",)
        return list_filter

    def get_list_display(self, request):
        list_display = ("id", "name", "provider", "organization", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("name", "provider", 'detail_link')
        return list_display

    def get_exclude(self, request, obj=None):
        exclude = ()
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            exclude = ("organization",)
        return exclude

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(organization=request.user.organization)
