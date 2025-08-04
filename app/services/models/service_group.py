from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class ServiceGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название группы')
    description = models.TextField(blank=True, null=True, verbose_name='Описание группы')
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Организация',
        related_name='service_groups'
    )
    services = models.ManyToManyField(
        'Service',
        blank=True,
        related_name='service_groups',
        verbose_name='Услуги'
    )

    total_price = models.DecimalField(
        verbose_name='Общая сумма',
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        editable=False
    )

    def recalc_total_price(self):
        self.total_price = (
            self.services.aggregate(s=Sum('price'))['s'] or 0
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа услуг'
        verbose_name_plural = 'Группы услуг'
