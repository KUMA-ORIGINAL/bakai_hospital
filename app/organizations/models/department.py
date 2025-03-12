from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название отдела")
    logo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Логотип отдела")
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, verbose_name="Организация")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
