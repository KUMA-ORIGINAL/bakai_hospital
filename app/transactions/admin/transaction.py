from django.contrib import admin
from django.db.models import Prefetch
from django.utils.html import format_html

from import_export.admin import ExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import RangeDateTimeFilter, RelatedDropdownFilter
from unfold.contrib.import_export.forms import ExportForm
from unfold.decorators import display

from account.models import ROLE_ADMIN, ROLE_DOCTOR, ROLE_ACCOUNTANT
from ..models import Transaction, TransactionService
from common.admin import BaseModelAdmin
from ..resources import TransactionResource


class TransactionServiceInline(TabularInline):
    model = TransactionService
    extra = 0
    fields = ("service", "service_price", 'quantity')
    readonly_fields = ('service', "service_price", 'quantity')

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('service')


@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin, BaseModelAdmin, ExportActionModelAdmin):
    search_fields = ("patient__first_name", "patient__last_name", "staff__first_name", "staff__last_name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    inlines = [TransactionServiceInline]
    resource_classes = (TransactionResource,)
    list_filter_submit = True
    list_select_related = ('patient', 'staff', 'organization')
    list_per_page = 25

    export_form_class = ExportForm

    def get_list_before_template(self, request):
        if request.user.role == ROLE_DOCTOR:
            return "transactions/transaction_list_before.html"
        return None

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        self.list_before_template = self.get_list_before_template(request)
        return super().changelist_view(request, extra_context=extra_context)

    def get_list_filter(self, request):
        list_filter = (
            ("patient", RelatedDropdownFilter),
            ("staff", RelatedDropdownFilter),
            "pay_method",
            "status",
            "organization",
            ("created_at", RangeDateTimeFilter)
        )
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_DOCTOR, ROLE_ACCOUNTANT):
            list_filter = (
                ("patient", RelatedDropdownFilter),
                ("staff", RelatedDropdownFilter),
                "pay_method",
                "status",
                ("created_at", RangeDateTimeFilter)
            )
        return list_filter

    def get_list_display(self, request):
        list_display = (
            "id", "patient", "staff", 'display_service', "total_price", "pay_method", "status", "created_at", "organization", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN,):
            list_display = ("id", "patient", "staff", "total_price", "pay_method", "status", "created_at", 'detail_link')
        elif request.user.role in (ROLE_DOCTOR, ROLE_ACCOUNTANT):
            list_display = ("id", "patient", "staff", "total_price", "pay_method", "status", "created_at", 'detail_link_view')
        return list_display

    @display(description="Услуги", dropdown=True)
    def display_service(self, instance):
        services = list(instance.services.all())
        total = len(services)

        if total == 0:
            return "-"

        items = []

        for service in services:
            title = format_html(
                """
                <div class="flex flex-row gap-2 items-center">
                    <span class="truncate">{}</span>
                </div>
                """,
                service.service.name,
            )
            items.append({"title": title})

        return {
            "title": f"{total} Услуг",
            "items": items,
            "striped": True,
            "width": 350,
        }

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            fields = (
                "created_at", "patient", "staff", "total_price", "comment", "phone_number",
                "pay_method", "status", "organization"
            )
        elif request.user.role in (ROLE_ADMIN, ROLE_DOCTOR, ROLE_ACCOUNTANT):
            fields = (
                "created_at", "patient", "staff", "total_price", "comment", "phone_number",
                "pay_method", "status",
            )
        return (
            (None, {"fields": fields}),
        )

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related('patient', 'staff', 'organization')

        qs = qs.prefetch_related(
            Prefetch(
                'services',
                queryset=TransactionService.objects.select_related('service')
            )
        )

        if request.user.is_superuser:
            return qs
        if request.user.role == ROLE_ADMIN:
            return qs.filter(organization=request.user.organization)
        elif request.user.role == ROLE_ACCOUNTANT:
            return qs.filter(organization=request.user.organization, status='success')
        elif request.user.role == ROLE_DOCTOR:
            return qs.filter(organization=request.user.organization, staff=request.user, status='success')
        return qs.none()

    def get_export_queryset(self, request):
        return (
            super()
            .get_export_queryset(request)
            .select_related(
                "patient",
                "staff",
                "organization",
            )
            .prefetch_related(
                "staff__rooms",  # ✅ M2M
                "staff__rooms__department",  # ✅ вложенный prefetch
            )
        )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False
