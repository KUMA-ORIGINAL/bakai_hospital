from django.db import models


class Patient(models.Model):
    GENDER_CHOICES = (
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('other', 'Другой'),
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия'
    )
    patronymic = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Отчество'
    )
    date_of_birth = models.DateField(
        verbose_name='Дата рождения'
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        verbose_name='Пол'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )
    inn = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="ИНН"
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Номер телефона'
    )
    passport_front_photo = models.ImageField(
        upload_to='patients/passport_photos/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Фото паспорта - передняя'
    )
    passport_back_photo = models.ImageField(
        upload_to='patients/passport_photos/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Фото паспорта - задняя'
    )
    passport_number = models.CharField(
        max_length=50,
        verbose_name='Номер паспорта'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Организация'
    )

    class Meta:
        verbose_name = 'Пациент'
        verbose_name_plural = 'Пациенты'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name} {self.patronymic}"
