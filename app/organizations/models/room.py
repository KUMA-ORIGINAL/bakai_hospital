from django.db import models


class Room(models.Model):
    room_number = models.CharField(max_length=20, verbose_name="Номер кабинета")
    floor = models.IntegerField(verbose_name="Этаж")
    building = models.ForeignKey('Building', on_delete=models.CASCADE, verbose_name="Здание")
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Отдел"
    )
    doctors = models.ManyToManyField(
        'account.User',
        blank=True,
        related_name='rooms',
        verbose_name='Врачи',
        limit_choices_to = {'role': 'doctor'},
    )
    services = models.ManyToManyField(
        'services.Service',
        blank=True,
        related_name='rooms_services',
        verbose_name='Услуги'
    )
    service_groups = models.ManyToManyField(
        'services.ServiceGroup',
        blank=True,
        related_name='rooms',
        verbose_name='Группы услуг'
    )

    def __str__(self):
        return f"Комната {self.room_number} - {self.building.name}"

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
