from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication."""

    def _create_user(self, email, password=None, **extra_fields):
        """Handles the common logic for user creation."""
        if not email:
            raise ValueError(_("The Email field is required"))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)


ROLE_ACCOUNTANT = 'accountant'  # Роль бухгалтера
ROLE_DOCTOR = 'doctor'  # Роль врача
ROLE_ADMIN = 'admin'  # Роль админа


class User(AbstractUser):
    ROLE_CHOICES = (
        (ROLE_ACCOUNTANT, "Бухгалтер"),
        (ROLE_DOCTOR, "Врач"),
        (ROLE_ADMIN, "Админ"),
    )

    STATUS_WORKING = 'working'  # Работает
    STATUS_FIRED = 'fired'  # Уволен

    STATUS_CHOICES = (
        (STATUS_WORKING, 'Работает'),
        (STATUS_FIRED, 'Уволен'),
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя сотрудника'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия сотрудника'
    )
    patronymic = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Отчество сотрудника'
    )
    position = models.CharField(
        max_length=255,
        verbose_name='Должность'
    )
    specialization = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Специализация'
    )
    email = models.EmailField(
        _("email address"),
        validators=[EmailValidator(_("Enter a valid email address."))],
        unique=True
    )
    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        validators=[
            RegexValidator(regex=r'^\+?1?\d{9,15}$', message=_("Enter a valid phone number."))],
        blank=True
    )
    birthdate = models.DateField(
        verbose_name='Дата рождения',
        blank=True,
        null=True
    )
    telegram_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name='Telegram ID'
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий'
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_WORKING,
        verbose_name='Статус (работает/уволен)'
    )
    photo = models.ImageField(
        upload_to='staffs/photos/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Фото сотрудника'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_DOCTOR,
        blank=True,
        verbose_name='Роль'
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Организация'
    )
    room = models.ForeignKey(
        'organizations.Room',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Кабинет'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Отдел"
    )

    username = None
    USERNAME_FIELD = "email"  # Use email as the unique identifier
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Required fields when creating a superuser

    objects = UserManager()

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
