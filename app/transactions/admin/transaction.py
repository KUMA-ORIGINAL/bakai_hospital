import logging

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Count, Q
from django.utils.html import format_html

from import_export.admin import ExportActionModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import StackedInline
from unfold.contrib.filters.admin import RangeDateTimeFilter, RelatedDropdownFilter
from unfold.contrib.import_export.forms import ExportForm
from unfold.decorators import display

from account.models import ROLE_ADMIN, ROLE_DOCTOR, ROLE_ACCOUNTANT
from ..models import Transaction, TransactionService
from common.admin import BaseModelAdmin
from ..resources import TransactionResource

logger = logging.getLogger(__name__)


class TransactionServiceInline(StackedInline):
    model = TransactionService
    extra = 0  # Не показывать пустые формы для добавления
    fields = ("service", "service_price", 'quantity', 'provider', 'service_provided', 'service_note')
    readonly_fields = ('service', "service_price", 'quantity', 'provider')

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        doctor_service_ids = set()

        if request.user.role == ROLE_DOCTOR:
            doctor_service_ids = set(request.user.services.values_list('id', flat=True))

        class CustomFormSet(FormSet):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.original_instances = {}
                if self.instance and self.instance.pk:
                    # Используем префетченные данные если доступны
                    if hasattr(self.instance, '_prefetched_services'):
                        self.original_instances = {
                            ts.pk: ts for ts in self.instance._prefetched_services
                        }
                    else:
                        # Делаем запрос только если не было префетча
                        self.original_instances = {
                            ts.pk: ts for ts in TransactionService.objects.filter(
                                transaction=self.instance
                            ).select_related('service', 'provider')
                        }

                # Оптимизация для врача
                if request.user.role == ROLE_DOCTOR:
                    for form in self.forms:
                        if not hasattr(form, 'instance') or not form.instance.pk:
                            continue

                        ts = form.instance
                        service_id = getattr(ts.service, 'id', None)
                        is_doctor_service = service_id in doctor_service_ids
                        service_name = getattr(ts.service, 'name', 'Неизвестная услуга')

                        # Логика отключения полей
                        if not is_doctor_service or (ts.service_provided and ts.provider):
                            for field in ['service_provided', 'service_note']:
                                if field in form.fields:
                                    form.fields[field].disabled = True
                                    form.fields[field].widget.attrs.update({
                                        'style': 'color: #666; cursor: not-allowed; opacity: 0.5;',
                                        'title': f'Услуга "{service_name}" - только для просмотра'
                                    })

        return CustomFormSet

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.role == ROLE_DOCTOR

    def has_add_permission(self, request, obj=None):
        return False  # Запрещаем создание новых услуг для всех

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('service', 'provider')


@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin, BaseModelAdmin, ExportActionModelAdmin):
    change_form_template = "admin/transactions/transaction/change_form.html"
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

    class Media:
        css = {
            'all': ('admin/admin_extra.css',)
        }

    def save_formset(self, request, form, formset, change):
        if request.user.role != ROLE_DOCTOR:
            return super().save_formset(request, form, formset, change)

        instances_to_update = []
        for obj in formset.save(commit=False):
            if not obj.pk:
                continue
            orig = formset.original_instances.get(obj.pk)
            if orig:
                if obj.service_provided and not orig.service_provided:
                    obj.provider = request.user
                else:
                    obj.provider = orig.provider
                    obj.service_provided = orig.service_provided
                instances_to_update.append(obj)

        if instances_to_update:
            TransactionService.objects.bulk_update(
                instances_to_update,
                ['provider', 'service_provided']
            )

        formset.save_m2m()

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
        elif request.user.role in (ROLE_ADMIN,):
            list_filter = (
                ("patient", RelatedDropdownFilter),
                ("staff", RelatedDropdownFilter),
                "pay_method",
                "status",
                ("created_at", RangeDateTimeFilter)
            )
        elif request.user.role in (ROLE_DOCTOR, ROLE_ACCOUNTANT):
            list_filter = (
                ("patient", RelatedDropdownFilter),
                ("staff", RelatedDropdownFilter),
                "pay_method",
                ("created_at", RangeDateTimeFilter)
            )
        return list_filter

    def get_list_display(self, request):
        list_display = (
            "id", "patient", "staff", 'display_service', "total_price", "pay_method", "status", "created_at",
            "organization", 'detail_link')
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN,):
            list_display = (
            "id", "patient", "staff", 'display_service', "total_price", "pay_method", "status", "created_at", 'detail_link')
        elif request.user.role == ROLE_ACCOUNTANT:
            list_display = (
            "id", "patient", "staff", 'display_service', "total_price", "pay_method", "status", "created_at", 'detail_link_view')
        elif request.user.role == ROLE_DOCTOR:
            list_display = (
            "id", "patient", "staff", 'display_service', "total_price", "pay_method", "status", "created_at", 'detail_link_view')
        return list_display

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        if request.user.role == ROLE_DOCTOR:
            # Все поля readonly, кроме service_provided и service_note
            all_fields = [
                "created_at", "patient", "staff", "total_price", "comment",
                "phone_number", "pay_method", "status", "payment_link", "organization"
            ]
            return self.readonly_fields + tuple(all_fields)
        return self.readonly_fields

    @display(description="Услуги", dropdown=True)
    def display_service(self, instance):
        services = getattr(instance, '_prefetched_services', [])
        total = len(services)

        if total == 0:
            return "-"

        items = [
            {
                "title": format_html(
                    '<div class="flex flex-row gap-2 items-center"><span class="truncate">{}</span></div>',
                    service.service.name,
                )
            }
            for service in services
        ]

        return {
            "title": f"{total} Услуг",
            "items": items,
            "striped": True,
            "width": 350,
        }

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            fields = (
                "created_at", "patient", "staff", "total_price", "phone_number",
                "pay_method", "status", 'payment_link', "organization"
            )
        elif request.user.role in (ROLE_ADMIN, ROLE_DOCTOR, ROLE_ACCOUNTANT):
            fields = (
                "created_at", "patient", "staff", "total_price", "phone_number",
                "pay_method", "status", 'payment_link',
            )
        return (
            (None, {"fields": fields}),
        )

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_object(self, request, object_id, from_field=None):
        queryset = self.get_queryset(request)
        model = queryset.model
        field = model._meta.pk if from_field is None else model._meta.get_field(from_field)
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('patient', 'staff', 'organization')

        services_prefetch = Prefetch(
            'services',
            queryset=TransactionService.objects.select_related('service', 'provider'),
            to_attr='_prefetched_services'
        )
        qs = qs.prefetch_related(services_prefetch)

        user = request.user

        if user.is_superuser:
            return qs
        if user.role == ROLE_ADMIN:
            return qs.filter(organization=user.organization)
        if user.role == ROLE_ACCOUNTANT:
            return qs.filter(organization=user.organization)
        if user.role == ROLE_DOCTOR:
            doctor_services = user.services.all()
            filter_conditions = Q(organization=user.organization)
            if doctor_services.exists():
                filter_conditions |= Q(
                    services__service__in=doctor_services,
                    organization=user.organization,
                ) | Q(
                    staff=user,
                    organization=user.organization,
                )
            else:
                filter_conditions &= Q(staff=user)
            return qs.filter(filter_conditions).distinct()

        return qs.none()

    def get_export_queryset(self, request):
        # Используем тот же оптимизированный queryset для экспорта
        base_qs = self.get_queryset(request)
        return base_qs.select_related(
            "patient",
            "staff",
            "organization",
        ).prefetch_related(
            Prefetch(
                'services',
                queryset=TransactionService.objects.select_related('service')
            )
        )

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.role == ROLE_DOCTOR:
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
