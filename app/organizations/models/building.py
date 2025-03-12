from django.db import models


class Building(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название здания")
    address = models.CharField(max_length=255, verbose_name="Адрес здания")
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, verbose_name="Организация")


    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Здание"
        verbose_name_plural = "Здания"