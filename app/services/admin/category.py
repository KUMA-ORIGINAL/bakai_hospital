from django.contrib import admin

from account.models import ROLE_ADMIN
from common.admin import BaseModelAdmin
from ..models import Category


@admin.register(Category)
class CategoryAdmin(BaseModelAdmin):
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 50

    def get_list_display(self, request):
        list_display = ("id", "name", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("name", 'detail_link')
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
        elif request.user.role == ROLE_ADMIN:
            return qs.filter(organization=request.user.organization)
