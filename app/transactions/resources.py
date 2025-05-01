from django.utils.translation import gettext_lazy as _

from import_export import resources, fields

from .models import Transaction


class TransactionResource(resources.ModelResource):
    patient = fields.Field(
        attribute="patient",
        column_name=Transaction._meta.get_field('patient').verbose_name,
    )
    staff = fields.Field(
        attribute="staff",
        column_name=Transaction._meta.get_field('staff').verbose_name,
    )
    total_price = fields.Field(
        attribute='total_price',
        column_name=Transaction._meta.get_field('total_price').verbose_name
    )
    comment = fields.Field(
        attribute='comment',
        column_name=Transaction._meta.get_field('comment').verbose_name
    )
    phone_number = fields.Field(
        attribute='phone_number',
        column_name=Transaction._meta.get_field('phone_number').verbose_name
    )
    pay_method = fields.Field(
        attribute='pay_method',
        column_name=Transaction._meta.get_field('pay_method').verbose_name
    )
    status = fields.Field(
        attribute='status',
        column_name=Transaction._meta.get_field('status').verbose_name
    )
    created_at = fields.Field(
        attribute='created_at',
        column_name=Transaction._meta.get_field('created_at').verbose_name
    )
    organization = fields.Field(
        attribute='organization',
        column_name=Transaction._meta.get_field('organization').verbose_name
    )
    services_summary = fields.Field(
        column_name=_("Состав чека"),
    )
    department = fields.Field(
        attribute='staff__room__department__name',
        column_name='Отдел'
    )

    class Meta:
        model = Transaction
        fields = ('id', 'patient', 'staff', 'total_price', 'services_summary', 'comment', 'phone_number',
                  'pay_method', 'status', 'created_at', 'department', 'organization')

    def dehydrate_created_at(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def dehydrate_services_summary(self, obj):
        return "; ".join(
            s.service.name for s in obj.services.all()
        )