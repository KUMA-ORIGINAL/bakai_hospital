from django.db import models


class TransactionService(models.Model):
    service_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена услуги", blank=True, null=True)

    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, verbose_name="Транзакция", related_name='services')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, verbose_name="Услуга")

    def __str__(self):
        return f"Услуга {self.service.name} для транзакции {self.transaction.id}"

    class Meta:
        verbose_name = "Услуга в транзакции"
        verbose_name_plural = "Услуги в транзакциях"

    def save(self, *args, **kwargs):
        self.service_price = self.service.price
        super().save(*args, **kwargs)
