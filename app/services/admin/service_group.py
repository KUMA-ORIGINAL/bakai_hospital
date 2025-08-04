from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from modeltranslation.admin import TabbedTranslationAdmin

from account.models import ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR
from ..models import ServiceGroup
from common.admin import BaseModelAdmin


class ServiceGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ServiceGroup
        fields = '__all__'

    def clean_services(self):
        services = self.cleaned_data.get('services')
        payout_accounts = set(s.payout_account_id for s in services if s.payout_account_id is not None)
        if services and len(payout_accounts) != 1:
            raise ValidationError(
                "У всех услуг в группе должен быть одинаковый счёт для выплат, и он не должен быть пустым."
            )
        return services


@admin.register(ServiceGroup)
class ServiceGroupAdmin(BaseModelAdmin, TabbedTranslationAdmin):
    form = ServiceGroupAdminForm
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ('total_price',)
    list_per_page = 50
    autocomplete_fields = ("services",)
    list_select_related = ("organization",)

    def get_list_filter(self, request):
        list_filter = ("organization",)
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT, ROLE_DOCTOR):
            list_filter = ()
        return list_filter

    def get_list_display(self, request):
        list_display = ("id", "name", "organization", "services_list", 'total_price', 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role == ROLE_ADMIN:
            list_display = ("name", "services_list", 'total_price', 'detail_link')
        elif request.user.role in (ROLE_ACCOUNTANT, ROLE_DOCTOR):
            list_display = ("name", "services_list", 'total_price', 'detail_link_view')
        return list_display

    def get_exclude(self, request, obj=None):
        exclude = ()
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_ACCOUNTANT):
            exclude = ('organization',)
        elif request.user.role == ROLE_DOCTOR:
            exclude = ('organization',)
        return exclude

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization

        super().save_model(request, obj, form, change)  # сохраняем сам объект
        form.save_m2m()  # сохраняем M2M-поля
        obj.recalc_total_price()  # теперь M2M уже заполнено
        obj.save(update_fields=['total_price'])

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(organization=request.user.organization)
        return qs.select_related('organization').prefetch_related('services')

    def services_list(self, obj):
        return ", ".join([s.name for s in obj.services.all()])
    services_list.short_description = "Услуги в группе"
