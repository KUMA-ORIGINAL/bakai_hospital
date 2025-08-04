from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TransactionService(models.Model):
    service_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена услуги", blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество", default=1)

    service_provided = models.BooleanField(
        default=False,
        verbose_name='Услуга оказана'
    )
    service_note = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий врача'
    )

    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, verbose_name="Транзакция", related_name='services')
    service = models.ForeignKey('services.Service', on_delete=models.PROTECT, verbose_name="Услуга")
    provider = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Кто оказал услугу",
        related_name='provided_services',
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Услуга ID={self.service_id} для транзакции #{self.transaction_id}"

    class Meta:
        verbose_name = "Услуга в транзакции"
        verbose_name_plural = "Услуги в транзакциях"

    def save(self, *args, **kwargs):
        self.service_price = self.service.price
        super().save(*args, **kwargs)
