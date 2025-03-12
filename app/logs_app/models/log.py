from django.db import models


class Log(models.Model):
    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('update', 'Изменение'),
        ('delete', 'Удаление')
    ]

    USER_TYPE_CHOICES = [
        ('patient', 'Пациент'),
        ('staff', 'Сотрудник')
    ]

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name="Действие"
    )
    entity = models.CharField(
        max_length=50,
        verbose_name="Сущность"
    )
    entity_id = models.IntegerField(
        verbose_name="ID сущности"
    )
    user_id = models.IntegerField(
        verbose_name="ID пользователя"
    )
    user_type = models.CharField(
        max_length=50,
        choices=USER_TYPE_CHOICES,
        verbose_name="Тип пользователя"
    )
    details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Дополнительные детали"
    )
    old_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Старые данные"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время действия"
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name="Организация"
    )

    def __str__(self):
        return f"Лог: {self.entity} - {self.action} - {self.created_at}"

    class Meta:
        verbose_name = "Лог"
        verbose_name_plural = "Логи"
        ordering = ['-created_at']  # Упорядочивание по времени (от новых к старым)

