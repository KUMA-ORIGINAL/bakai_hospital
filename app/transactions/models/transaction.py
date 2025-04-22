from django.db import models
from simple_history.models import HistoricalRecords


class Transaction(models.Model):
    patient = models.ForeignKey('account.Patient', on_delete=models.CASCADE, verbose_name="Пациент")
    staff = models.ForeignKey('account.User', on_delete=models.CASCADE, verbose_name="Сотрудник")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма", blank=True, null=True)
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    phone_number = models.CharField(max_length=20, verbose_name="Номер телефона")
    pay_method = models.CharField(
        max_length=50,
        choices=[('bakai_bank', 'Bakai Bank')],
        verbose_name="Способ оплаты",
        default='bakai_bank'
    )
    status = models.CharField(
        max_length=50,
        choices=[('success', 'Оплачено'), ('pending', 'В ожидании'), ('failed', 'Не удалось')],
        verbose_name="Статус оплаты",
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата транзакции")
    history = HistoricalRecords()
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Организация',
        related_name='transactions'
    )

    def __str__(self):
        return f"Транзакция {self.id}"

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
        ordering = ['-created_at']  # Упорядочивание по дате транзакции (от новых к старым)
