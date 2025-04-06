from django.db import models


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Название категории'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Организация',
        related_name='categories'
    )

    class Meta:
        verbose_name = 'Категория услуги'
        verbose_name_plural = 'Категории услуг'

    def __str__(self):
        return self.name
