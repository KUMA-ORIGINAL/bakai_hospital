from import_export import resources, fields
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch
from .models import Transaction, TransactionService


class TransactionResource(resources.ModelResource):
    patient = fields.Field(attribute="patient", column_name="Пациент")
    staff = fields.Field(attribute="staff", column_name="Сотрудник")
    total_price = fields.Field(attribute='total_price', column_name="Итоговая сумма")
    comment = fields.Field(attribute='comment', column_name="Комментарий")
    phone_number = fields.Field(attribute='phone_number', column_name="Телефон")
    pay_method = fields.Field(attribute='pay_method', column_name="Тип оплаты")
    status = fields.Field(attribute='status', column_name="Статус")
    created_at = fields.Field(attribute='created_at', column_name="Дата")
    organization = fields.Field(attribute='organization', column_name="Организация")

    services_summary = fields.Field(column_name=_("Состав чека"))
    department = fields.Field(column_name="Отдел")

    class Meta:
        model = Transaction
        fields = (
            'id', 'patient', 'staff', 'services_summary', 'total_price',
            'comment', 'phone_number', 'pay_method', 'status',
            'created_at', 'department', 'organization',
        )

    def dehydrate_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def dehydrate_services_summary(self, obj):
        return "; \n".join(
            f"{s.service.name} x{s.quantity} — {s.service_price} сом"
            for s in obj.services.all()
        )

    def dehydrate_department(self, obj):
        try:
            return obj.staff.rooms.department.name
        except AttributeError:
            return ""
