from django.db import models


class Room(models.Model):
    room_number = models.CharField(max_length=20, verbose_name="Номер кабинета")
    floor = models.IntegerField(verbose_name="Этаж")
    building = models.ForeignKey('Building', on_delete=models.CASCADE, verbose_name="Здание")
    services = models.ManyToManyField(
        'services.Service',
        blank=True,
        related_name='services',
        verbose_name='Услуги'
    )

    def __str__(self):
        return f"Комната {self.room_number} - {self.building.name}"

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
