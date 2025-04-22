from django.contrib import admin

from common.admin import BaseModelAdmin
from transactions.models import Transaction
from ..models import Patient, ROLE_ADMIN, ROLE_DOCTOR


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    fields = ('created_at', 'staff', 'total_price', 'status', 'pay_method')
    readonly_fields = ('created_at', 'staff', 'total_price', 'status', 'pay_method')
    can_delete = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('staff')


@admin.register(Patient)
class PatientAdmin(BaseModelAdmin):
    search_fields = ('first_name', 'last_name', 'patronymic', 'inn', 'phone_number', 'passport_number')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    inlines = (TransactionInline,)

    def get_list_filter(self, request):
        list_filter = ('gender', 'organization', 'created_at')
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_DOCTOR):
            list_filter = ('gender', 'created_at')
        return list_filter

    def get_list_display(self, request):
        list_display = (
            'first_name', 'last_name', 'patronymic', 'date_of_birth', 'gender', 'inn', 'phone_number',
            'organization', 'detail_link'
        )
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_DOCTOR):
            list_display = (
                'first_name', 'last_name', 'patronymic', 'date_of_birth', 'gender', 'inn', 'phone_number', 'detail_link'
            )
        return list_display

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            (None, {
                'fields': (
                    'first_name', 'last_name', 'patronymic', 'date_of_birth', 'gender', 'inn', 'phone_number',
                    'passport_number')
            }),
            ('Дополнительно', {
                'fields': ('photo', 'comment', 'passport_front_photo', 'passport_back_photo', 'organization', 'created_at'),
            }),
        )
        if request.user.is_superuser:
            pass
        elif request.user.role in (ROLE_ADMIN, ROLE_DOCTOR):
            fieldsets[1][1]['fields'] = ('photo', 'comment', 'passport_front_photo', 'passport_back_photo', 'created_at')
        return fieldsets

    def save_model(self, request, obj, form, change):
        if request.user.role == ROLE_ADMIN:
            obj.organization = request.user.organization
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.role in (ROLE_ADMIN, ROLE_DOCTOR):
            return qs.filter(organization=request.user.organization)
