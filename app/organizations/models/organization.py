from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название организации")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    phone_number = models.CharField(max_length=20, verbose_name="Телефонный номер")
    email = models.EmailField(verbose_name="Электронная почта")
    logo = models.ImageField(upload_to='organizations/logos/%Y/%m', blank=True, null=True, verbose_name="Логотип")
    website = models.CharField(max_length=255, blank=True, null=True, verbose_name="Вебсайт")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"