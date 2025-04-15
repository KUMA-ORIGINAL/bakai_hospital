from django.db import models


class PayoutAccount(models.Model):
    PROVIDER_CHOICES = [
        ('Bakai', 'Bakai'),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Название счёта'
    )
    provider = models.CharField(
        max_length=100,
        choices=PROVIDER_CHOICES,
        verbose_name='Платёжная система'
    )
    payout_token = models.TextField(
        verbose_name='Токен для выплат'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Организация',
        related_name='payout_accounts'
    )

    def __str__(self):
        return f'{self.name} ({self.provider})'

    class Meta:
        verbose_name = 'Счёт для выплат'
        verbose_name_plural = 'Счета для выплат'
